import argparse
import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import setup_repository as setup


class FakeAPI:
    def __init__(self):
        self.repo = {'full_name': 'example/project', 'visibility': 'private',
                     'default_branch': 'main', 'permissions': {'admin': True},
                     'allow_merge_commit': True, 'allow_squash_merge': True,
                     'delete_branch_on_merge': False, 'allow_update_branch': False,
                     'has_projects': True, 'has_downloads': True}
        self.rules = []
        self.writes = []
        self.green = True
        self.ignore_patch = False
        self.reporting = False

    def __call__(self, method, endpoint, payload=None):
        if endpoint.endswith('/private-vulnerability-reporting'):
            if method == 'GET':
                return {'enabled': self.reporting}
            self.writes.append((method, endpoint, payload))
            self.reporting = method == 'PUT'
            return None
        if method != 'GET':
            self.writes.append((method, endpoint, copy.deepcopy(payload)))
            if method == 'POST':
                self.rules.append(dict(copy.deepcopy(payload), id=len(self.rules) + 1, source_type='Repository'))
            elif method == 'PUT':
                i = int(endpoint.rsplit('/', 1)[1])
                self.rules = [dict(copy.deepcopy(payload), id=i, source_type='Repository') if r['id'] == i else r for r in self.rules]
            elif method == 'PATCH' and not self.ignore_patch:
                self.repo.update(payload)
            return {}
        if '/check-runs?' in endpoint:
            return {'check_runs': [{'name': 'Repository integrity', 'app': {'id': 15368},
                                   'status': 'completed', 'conclusion': 'success' if self.green else 'failure'}]}
        if '/branches/' in endpoint:
            return {'commit': {'sha': 'abc'}}
        if '/rulesets?' in endpoint:
            return copy.deepcopy(self.rules)
        if '/rulesets/' in endpoint:
            return copy.deepcopy(next(r for r in self.rules if r['id'] == int(endpoint.rsplit('/', 1)[1])))
        return copy.deepcopy(self.repo)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeAPI()
        self.args = argparse.Namespace(repo='example/project', config=setup.CONFIG,
                                       apply=False, check=False, update_existing=False)

    def run_setup(self):
        with redirect_stdout(io.StringIO()):
            return setup.run(self.args, self.api)

    def test_preview_never_writes(self):
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(self.api.writes, [])

    def test_check_returns_drift_without_writes(self):
        self.args.check = True
        self.assertEqual(self.run_setup(), 1)
        self.assertEqual(self.api.writes, [])

    def test_apply_verify_and_second_run_is_noop(self):
        self.args.apply = True
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(len(self.api.writes), 6)
        self.assertEqual(self.api.writes[-1][0], 'PATCH')
        self.api.writes.clear()
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(self.api.writes, [])

    def test_failed_check_blocks_all_writes(self):
        self.args.apply = True
        self.api.green = False
        with self.assertRaisesRegex(setup.SetupError, 'has not succeeded'):
            self.run_setup()
        self.assertEqual(self.api.writes, [])

    def test_non_admin_blocks_all_writes(self):
        self.args.apply = True
        self.api.repo['permissions']['admin'] = False
        with self.assertRaisesRegex(setup.SetupError, 'Administrative'):
            self.run_setup()
        self.assertEqual(self.api.writes, [])

    def test_existing_rule_changes_require_explicit_flag(self):
        rule = copy.deepcopy(setup.load_config(setup.CONFIG)['rulesets'][0])
        rule.update(id=1, source_type='Repository', enforcement='disabled')
        self.api.rules = [rule]
        self.args.apply = True
        with self.assertRaisesRegex(setup.SetupError, 'named ruleset differs'):
            self.run_setup()
        self.assertEqual(self.api.writes, [])
        self.args.update_existing = True
        self.assertEqual(self.run_setup(), 0)

    def test_unrelated_rules_are_preserved(self):
        self.api.rules = [{'name': 'Other rule', 'id': 10, 'source_type': 'Repository'}]
        self.args.apply = True
        self.run_setup()
        self.assertEqual(self.api.rules[0]['name'], 'Other rule')

    def test_preview_names_unmanaged_rulesets_without_writing(self):
        self.api.rules = [{'name': 'main', 'id': 10, 'source_type': 'Repository', 'target': 'branch',
                           'enforcement': 'active',
                           'conditions': {'ref_name': {'include': ['~DEFAULT_BRANCH'], 'exclude': []}}}]
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(setup.run(self.args, self.api), 0)
        self.assertIn('unmanaged ruleset "main" (branch: ~DEFAULT_BRANCH; active)', output.getvalue())
        self.assertEqual(self.api.writes, [])

    def test_public_repository_enables_vulnerability_reporting_once(self):
        self.api.repo['visibility'] = 'public'
        self.args.apply = True
        self.assertEqual(self.run_setup(), 0)
        self.assertIn(('PUT', 'repos/example/project/private-vulnerability-reporting', None),
                      self.api.writes)
        self.assertEqual(self.api.writes[-1][0], 'PATCH')
        self.api.writes.clear()
        self.assertEqual(self.run_setup(), 0)
        self.assertEqual(self.api.writes, [])

    def test_private_repository_skips_vulnerability_reporting_with_a_note(self):
        self.args.apply = True
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(setup.run(self.args, self.api), 0)
        self.assertIn('available only for public repositories', output.getvalue())
        self.assertFalse(any('vulnerability' in endpoint for _, endpoint, _ in self.api.writes))

    def test_check_reports_disabled_vulnerability_reporting_as_drift(self):
        self.api.repo['visibility'] = 'public'
        self.args.apply = True
        self.run_setup()
        self.api.reporting = False
        self.args.apply, self.args.check = False, True
        self.assertEqual(self.run_setup(), 1)

    def test_duplicate_names_rejected_before_writes(self):
        name = setup.load_config(setup.CONFIG)['rulesets'][0]['name']
        self.api.rules = [{'name': name, 'id': 1}, {'name': name, 'id': 2}]
        with self.assertRaisesRegex(setup.SetupError, 'Ambiguous'):
            self.run_setup()
        self.assertFalse(self.api.writes)

    def test_readback_detects_ignored_changes(self):
        self.args.apply = True
        self.api.ignore_patch = True
        with self.assertRaisesRegex(setup.SetupError, 'Read-back'):
            self.run_setup()

    def test_pagination_reads_beyond_first_page(self):
        calls = []
        def call(method, endpoint):
            calls.append(endpoint)
            return list(range(100)) if endpoint.endswith('&page=1') else [100]
        self.assertEqual(len(setup.pages(call, 'repos/x/y/rulesets?includes_parents=false')), 101)
        self.assertEqual(len(calls), 2)

    def test_order_is_not_drift_but_extra_rule_is(self):
        r = copy.deepcopy(setup.load_config(setup.CONFIG)['rulesets'][-1])
        reordered = copy.deepcopy(r)
        reordered['rules'].reverse()
        self.assertEqual(setup.rule_spec(r), setup.rule_spec(reordered))
        reordered['rules'].append({'type': 'creation'})
        self.assertNotEqual(setup.rule_spec(r), setup.rule_spec(reordered))

    def test_cli_uses_explicit_method_host_and_stdin(self):
        result = argparse.Namespace(returncode=0, stdout='{}', stderr='')
        with patch.object(setup.subprocess, 'run', return_value=result) as run:
            setup.api('PATCH', 'repos/a/b', {'has_projects': False})
            cmd = run.call_args.args[0]
            self.assertIn('github.com', cmd)
            self.assertIn('PATCH', cmd)
            self.assertEqual(cmd[-2:], ['--input', '-'])
            self.assertEqual(run.call_args.kwargs['input'], '{"has_projects": false}')

    def test_api_error_does_not_print_server_detail(self):
        result = argparse.Namespace(returncode=1, stdout='', stderr='secret token HTTP 403')
        with patch.object(setup.subprocess, 'run', return_value=result):
            with self.assertRaises(setup.SetupError) as caught:
                setup.api('GET', 'repos/a/b')
        self.assertIn('HTTP 403', str(caught.exception))
        self.assertNotIn('secret token', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
