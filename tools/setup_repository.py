#!/usr/bin/env python3
"""Apply the portable baseline through an authenticated GitHub CLI (github.com)."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

CONFIG = Path(__file__).resolve().parents[1] / 'docs/setup/repository-settings.json'
RULE_KEYS = ('name', 'target', 'enforcement', 'conditions', 'rules', 'bypass_actors')
GENERAL_KEYS = {'delete_branch_on_merge', 'allow_update_branch', 'has_projects', 'has_downloads'}


class SetupError(Exception):
    pass


def api(method, endpoint, payload=None):
    command = ['gh', 'api', '--hostname', 'github.com', '--method', method,
               '-H', 'Accept: application/vnd.github+json',
               '-H', 'X-GitHub-Api-Version: 2022-11-28', endpoint]
    if payload is not None:
        command += ['--input', '-']
    # Never inherit HTTP debug logging: it can expose authentication headers.
    env = dict(os.environ)
    env.pop('GH_DEBUG', None)
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, env=env, check=False)
    if result.returncode:
        # Do not print CLI stderr (may contain sensitive server or credential detail).
        match = re.search(r'HTTP (\d{3})', result.stderr)
        status = match.group(1) if match else 'unknown'
        raise SetupError(f'{method} {endpoint} failed (HTTP {status}). Check gh authentication, '
                         'repository access, Administration permissions and plan availability. '
                         'No automatic rollback is performed; rerun preview to inspect partial changes.')
    return json.loads(result.stdout) if result.stdout.strip() else None


def pages(call, endpoint, key=None):
    result = []
    page = 1
    while True:
        separator = '&' if '?' in endpoint else '?'
        value = call('GET', f'{endpoint}{separator}per_page=100&page={page}')
        batch = value[key] if key else value
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def canonical(value):
    """Rule arrays are sets for this baseline; ignore API ordering, not values."""
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return sorted((canonical(x) for x in value), key=lambda x: json.dumps(x, sort_keys=True))
    return value


def rule_spec(rule):
    # Ignore response metadata, but preserve unknown rules/parameters in comparison.
    return canonical({k: rule.get(k, [] if k == 'bypass_actors' else None) for k in RULE_KEYS})


def load_config(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    if set(value) != {'schema_version', 'repository', 'rulesets'} or value['schema_version'] != 1:
        raise SetupError('Unsupported configuration schema.')
    if set(value['repository']) != GENERAL_KEYS or any(type(v) is not bool for v in value['repository'].values()):
        raise SetupError('Configuration must contain exactly the four documented boolean repository settings.')
    names = []
    for rule in value['rulesets']:
        if set(rule) != set(RULE_KEYS) or rule['target'] not in ('branch', 'tag') or rule['enforcement'] != 'active':
            raise SetupError('Invalid baseline ruleset.')
        if rule['bypass_actors'] or rule['conditions']['ref_name']['exclude']:
            raise SetupError('Baseline must not contain bypass actors or excluded refs.')
        names.append(rule['name'])
    if len(names) != 5 or len(set(names)) != 5:
        raise SetupError('Expected five uniquely named baseline rulesets.')
    return value


def inspect(call, repo, config, report=True):
    root = f'repos/{repo}'
    metadata = call('GET', root)
    if metadata.get('archived') or metadata.get('disabled'):
        raise SetupError('Destination is archived or disabled.')
    if not metadata.get('permissions', {}).get('admin'):
        raise SetupError('Administrative access to the destination is required.')
    current = pages(call, root + '/rulesets?includes_parents=false')
    inherited = pages(call, root + '/rulesets?includes_parents=true')
    print(f'Destination: {metadata["full_name"]}; visibility: {metadata["visibility"]}; '
          f'default branch: {metadata["default_branch"]}')
    if report and any(r.get('source_type') != 'Repository' for r in inherited):
        print('NOTE: inherited rules also apply; they are not modified or certified by this script.')
    if report:
        report_unmanaged(call, root, current, config)
    plan = []
    for desired in config['rulesets']:
        matches = [r for r in current if r['name'] == desired['name']]
        if len(matches) > 1:
            raise SetupError(f'Ambiguous duplicate ruleset name: {desired["name"]}')
        if not matches:
            plan.append(('POST', root + '/rulesets', desired))
        else:
            endpoint = root + '/rulesets/' + str(matches[0]['id'])
            actual = call('GET', endpoint)
            if rule_spec(actual) != rule_spec(desired):
                plan.append(('PUT', endpoint, desired))
    changes = {k: v for k, v in config['repository'].items() if metadata.get(k) != v}
    # Install protection first, then enable branch cleanup.
    if changes:
        plan.append(('PATCH', root, changes))
    return metadata, plan


def report_unmanaged(call, root, current, config):
    """Name repository rulesets outside the baseline; they stay active alongside it."""
    managed = {rule['name'] for rule in config['rulesets']}
    for ruleset in current:
        if ruleset.get('source_type', 'Repository') != 'Repository' or ruleset['name'] in managed:
            continue
        detail = call('GET', f'{root}/rulesets/{ruleset["id"]}')
        refs = ', '.join(((detail.get('conditions') or {}).get('ref_name') or {}).get('include') or [])
        print(f'NOTE: unmanaged ruleset "{ruleset["name"]}" '
              f'({detail.get("target", "unknown target")}: {refs or "no ref conditions"}; '
              f'{detail.get("enforcement", "unknown enforcement")}) stays active. This script '
              'never changes or deletes it; delete it in the repository settings if a managed '
              'ruleset replaces it.')


def check_prerequisites(call, repo, metadata, config):
    root = f'repos/{repo}'
    branch = call('GET', root + '/branches/' + quote(metadata['default_branch'], safe=''))
    checks = pages(call, root + '/commits/' + branch['commit']['sha'] + '/check-runs?filter=latest', 'check_runs')
    required = [check for r in config['rulesets'] for rule in r['rules']
                if rule['type'] == 'required_status_checks'
                for check in rule['parameters']['required_status_checks']]
    for required_check in required:
        if not any(c['name'] == required_check['context'] and
                   c.get('app', {}).get('id') == required_check['integration_id'] and
                   c.get('conclusion') == 'success' and c.get('status') == 'completed' for c in checks):
            raise SetupError('Required GitHub Actions check has not succeeded on the current default-branch '
                             'HEAD. Enable Actions and run Repository integrity before applying protection.')
    if not metadata.get('allow_merge_commit'):
        raise SetupError('Merge commits must be enabled before applying these rules.')
    if not metadata.get('allow_squash_merge'):
        raise SetupError('Squash merging must be enabled for the release-branch baseline.')


def run(args, call=api):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+', args.repo) or args.repo.split('/')[1] in ('.', '..'):
        raise SetupError('Destination must be an explicit owner/repository on github.com.')
    config = load_config(args.config)
    metadata, plan = inspect(call, args.repo, config)
    if not plan:
        print('VERIFIED: all documented settings match. Unmanaged settings are outside this verification.')
        return 0
    for method, endpoint, payload in plan:
        print(f'{method} {endpoint}\n{json.dumps(payload, indent=2)}')
    if args.check:
        print('DRIFT: documented settings do not match.')
        return 1
    if not args.apply:
        print('PREVIEW ONLY: no changes made. Use --apply to execute this plan.')
        return 0
    if any(method == 'PUT' for method, _, _ in plan) and not args.update_existing:
        raise SetupError('A named ruleset differs. Review the preview, then use --update-existing '
                         'to replace that entire named ruleset. Additional rules in it will be removed.')
    check_prerequisites(call, args.repo, metadata, config)
    for method, endpoint, payload in plan:
        call(method, endpoint, payload)
        print(f'Applied {method} {endpoint}')
    _, remaining = inspect(call, args.repo, config, report=False)
    if remaining:
        raise SetupError('Read-back verification failed; rerun preview to inspect remaining differences.')
    print('VERIFIED: all documented settings match after apply.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='Explicit destination owner/repository')
    parser.add_argument('--config', type=Path, default=CONFIG)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='Apply changes, then verify')
    mode.add_argument('--check', action='store_true', help='Read-only verification; exit 1 for drift')
    parser.add_argument('--update-existing', action='store_true', help='Allow replacement of differing named rulesets')
    args = parser.parse_args()
    if args.update_existing and not args.apply:
        parser.error('--update-existing requires --apply')
    try:
        return run(args)
    except (SetupError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
