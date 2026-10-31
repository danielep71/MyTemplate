"""Governance invariants of the workflows and Dependabot, read with a real YAML parser.

The parser is pinned in .github/requirements.txt; install it with
``python -m pip install -r .github/requirements.txt``. Without it the tests
are skipped locally and fail in GitHub Actions.
"""

import os
import re
from pathlib import Path
import unittest

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without the parser
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / '.github/workflows'
REQUIRED_JOB = ('repository-integrity.yml', 'repository-integrity')
REQUIRED_CHECK = 'Repository integrity'
# The only jobs that may write, and what each may write.
WRITE_PERMISSIONS = {
    ('labels-sync.yml', 'reconcile'): {'issues'},
    ('traffic-history.yml', 'collect'): {'contents'},
    ('traffic-history.yml', 'alert'): {'issues'},
    ('pr-milestones.yml', 'reconcile'): {'pull-requests'},
}
PINNED = re.compile(r'^[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}$')


def load(path):
    document = yaml.safe_load(path.read_text(encoding='utf-8'))
    # YAML 1.1 reads the bare key "on" as True.
    if True in document:
        document['on'] = document.pop(True)
    return document


def workflows():
    return {path.name: load(path) for path in sorted(WORKFLOWS.glob('*.yml'))}


@unittest.skipIf(yaml is None and not os.environ.get('GITHUB_ACTIONS'),
                 'PyYAML is not installed: python -m pip install -r .github/requirements.txt')
class WorkflowControlTests(unittest.TestCase):
    def test_parser_is_available(self):
        self.assertIsNotNone(yaml, 'install .github/requirements.txt before running the tests')

    def test_actions_are_pinned_and_checkouts_drop_credentials(self):
        for name, document in workflows().items():
            for job_id, job in document['jobs'].items():
                for step in job.get('steps', []):
                    if 'uses' not in step:
                        continue
                    with self.subTest(workflow=name, job=job_id, uses=step['uses']):
                        self.assertRegex(step['uses'], PINNED)
                        if step['uses'].startswith('actions/checkout@'):
                            self.assertIs((step.get('with') or {}).get('persist-credentials'), False)

    def test_every_job_has_a_timeout_and_permissions_are_explicit(self):
        for name, document in workflows().items():
            with self.subTest(workflow=name):
                self.assertIn('permissions', document)
            for job_id, job in document['jobs'].items():
                with self.subTest(workflow=name, job=job_id):
                    self.assertIsInstance(job.get('timeout-minutes'), int)

    def test_only_the_listed_jobs_write(self):
        def writes(permissions):
            if permissions in ('write-all', 'read-all'):
                return {permissions}
            return {scope for scope, level in (permissions or {}).items() if level == 'write'}

        for name, document in workflows().items():
            with self.subTest(workflow=name, level='workflow'):
                self.assertEqual(writes(document['permissions']), set())
            for job_id, job in document['jobs'].items():
                with self.subTest(workflow=name, job=job_id):
                    self.assertEqual(writes(job.get('permissions')),
                                     WRITE_PERMISSIONS.get((name, job_id), set()))

    def test_required_check_runs_unconditionally_on_every_branch(self):
        name, job_id = REQUIRED_JOB
        document = workflows()[name]
        for event in ('pull_request', 'push'):
            with self.subTest(event=event):
                self.assertIn(event, document['on'])
                self.assertFalse(document['on'][event], f'{event} must have no branch or path filters')
        job = document['jobs'][job_id]
        self.assertNotIn('if', job)
        self.assertNotIn('strategy', job)
        # The rulesets require this name; tests/test_setup_repository.py checks the
        # settings file against it while the setup tooling is kept.
        self.assertEqual(job['name'], REQUIRED_CHECK)

    def test_live_label_reconciliation_runs_only_on_the_default_branch(self):
        condition = workflows()['labels-sync.yml']['jobs']['reconcile']['if']
        self.assertIn("github.event_name != 'pull_request'", condition)
        self.assertIn('github.event.repository.default_branch', condition)

    def test_milestone_workflow_never_runs_pull_request_code(self):
        document = workflows()['pr-milestones.yml']
        self.assertEqual(set(document['on']), {'push', 'pull_request_target', 'schedule', 'workflow_dispatch'})
        self.assertEqual(document['on']['pull_request_target'],
                         {'types': ['opened', 'reopened', 'edited', 'milestoned']})
        self.assertEqual(document['permissions'], {})
        job = document['jobs']['reconcile']
        self.assertEqual(job['permissions'], {'pull-requests': 'write'})
        self.assertIn('github.event.repository.default_branch', job['if'])
        self.assertEqual(len(job['steps']), 1)
        step = job['steps'][0]
        self.assertEqual(set(step), {'name', 'env', 'run'})
        self.assertEqual(step['env'], {'GH_TOKEN': '${{ github.token }}'})
        self.assertNotIn('${{', step['run'])

    def test_dependabot_covers_each_pinned_dependency_once(self):
        document = yaml.safe_load((ROOT / '.github/dependabot.yml').read_text(encoding='utf-8'))
        self.assertEqual(document['version'], 2)
        updates = document['updates']
        self.assertEqual(sorted((u['package-ecosystem'], u['directory']) for u in updates),
                         [('github-actions', '/'), ('pip', '/.github')])
        for update in updates:
            with self.subTest(ecosystem=update['package-ecosystem']):
                self.assertNotIn('milestone', update)
                self.assertEqual([label for label in update['labels'] if label in {'P1', 'P2', 'P3'}], ['P3'])


def milestone_script():
    run = workflows()['pr-milestones.yml']['jobs']['reconcile']['steps'][0]['run']
    return run.split("<<'PY'\n", 1)[1].rsplit('PY', 1)[0]


class FakeGitHub:
    def __init__(self, pulls, issues=()):
        self.items = {pull['number']: dict(pull, pull_request={}) for pull in pulls}
        self.items.update({issue['number']: dict(issue) for issue in issues})
        self.patches = []

    def __call__(self, method, path, data=None):
        if path.startswith('/repos/o/r/pulls?'):
            page = int(re.search(r'[?&]page=(\d+)', path).group(1))
            pulls = [item for item in self.items.values() if 'pull_request' in item]
            return pulls[(page - 1) * 100:page * 100]
        number = int(path.rsplit('/', 1)[1])
        if method == 'PATCH':
            self.patches.append(number)
            self.items[number]['milestone'] = data['milestone']
        return dict(self.items[number])


@unittest.skipIf(yaml is None and not os.environ.get('GITHUB_ACTIONS'),
                 'PyYAML is not installed: python -m pip install -r .github/requirements.txt')
class MilestoneScriptTests(unittest.TestCase):
    def reconcile(self):
        namespace = {'__name__': 'milestones'}
        exec(milestone_script(), namespace)  # trusted: the script under test, from this repository
        return namespace['reconcile']

    def test_pull_request_event_clears_only_that_pull_request(self):
        api = FakeGitHub([{'number': 1, 'milestone': {'title': 'v1'}},
                          {'number': 2, 'milestone': {'title': 'v1'}}])
        self.reconcile()(api, 'o/r', {'number': 1, 'pull_request': {}})
        self.assertEqual(api.patches, [1])
        self.assertIsNotNone(api.items[2]['milestone'])

    def test_scan_clears_every_pull_request_and_never_touches_issues(self):
        pulls = [{'number': n, 'milestone': {'title': 'v1'} if n % 2 else None} for n in range(1, 151)]
        api = FakeGitHub(pulls, issues=[{'number': 500, 'milestone': {'title': 'v1'}}])
        self.reconcile()(api, 'o/r', {'schedule': '17 3 * * *'})
        self.assertEqual(api.patches, list(range(1, 151, 2)))
        self.assertIsNotNone(api.items[500]['milestone'])

    def test_an_issue_number_is_refused(self):
        api = FakeGitHub([], issues=[{'number': 7, 'milestone': {'title': 'v1'}}])
        with self.assertRaisesRegex(ValueError, 'Refusing to change an issue'):
            self.reconcile()(api, 'o/r', {'number': 7, 'pull_request': {}})
        self.assertEqual(api.patches, [])


if __name__ == '__main__':
    unittest.main()
