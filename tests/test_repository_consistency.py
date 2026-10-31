"""Cross-file contracts for the template's public label catalogue."""

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CatalogueDocumentationTests(unittest.TestCase):
    def test_guide_matches_label_names_colors_and_descriptions(self):
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        guide = (ROOT / 'docs/repo_governance/ISSUE_LABELS.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| `([^`]+)` \| `#([0-9A-F]+)` \| (.+) \|$', guide, re.M)
        expected = [(label['name'], label['color'], label['description'])
                    for label in manifest['labels']]
        self.assertEqual(rows, expected)

    def test_usage_guide_covers_every_label_once(self):
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        guide = (ROOT / 'docs/repo_governance/ISSUE_LABELS.md').read_text(encoding='utf-8')
        section = re.search(r'^## 🧭 Using the labels$(.*?)^## ', guide, re.M | re.S).group(1)
        names = re.findall(r'^\| `([^`]+)` \|', section, re.M)
        self.assertEqual(sorted(names, key=str.lower),
                         sorted((label['name'] for label in manifest['labels']), key=str.lower))

    def test_documented_label_counts_match_the_catalogue(self):
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        expected = str(len(manifest['labels']))
        pattern = re.compile(r'labels-(\d+)-|\b(\d+) (?:issue )?labels\b', re.I)
        counts = []
        for path in sorted(ROOT.glob('**/*.md')):
            if '.git' in path.parts:
                continue
            text = path.read_text(encoding='utf-8')
            counts += [(path.relative_to(ROOT).as_posix(), badge or prose)
                       for badge, prose in pattern.findall(text)]
        self.assertTrue(counts, 'no documented label counts found')
        self.assertEqual([item for item in counts if item[1] != expected], [])


def yaml_list(text, key):
    """Return the block-list items under ``key:`` in a simple YAML file."""
    items, indent = [], None
    for line in text.splitlines():
        stripped = line.strip()
        if indent is None:
            if stripped == f'{key}:':
                indent = len(line) - len(line.lstrip())
            continue
        if stripped.startswith('- ') and len(line) - len(line.lstrip()) > indent:
            items.append(stripped[2:].strip().strip('"\''))
        elif stripped:
            indent = None
    return items


class DependabotTests(unittest.TestCase):
    def test_labels_exist_and_assignee_matches_the_issue_forms(self):
        text = (ROOT / '.github/dependabot.yml').read_text(encoding='utf-8')
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        catalogue = {label['name'] for label in manifest['labels']}
        labels = yaml_list(text, 'labels')
        self.assertTrue(labels)
        self.assertEqual([label for label in labels if label not in catalogue], [])
        form = (ROOT / '.github/ISSUE_TEMPLATE/bug.yml').read_text(encoding='utf-8')
        assignee = re.search(r'^assignees:\s*\[\s*"?([^",\]]+)"?\s*\]', form, re.M).group(1)
        self.assertEqual(set(yaml_list(text, 'assignees')), {assignee})


MARKDOWN_LINK = re.compile(r'\]\(([^)\s]+)\)|^\[[^\]]+\]:\s*(\S+)', re.M)
FENCE = re.compile(r'^```.*?^```', re.M | re.S)


class MarkdownLinkTests(unittest.TestCase):
    def test_relative_links_point_to_existing_files(self):
        checked, broken = 0, []
        for path in sorted(ROOT.rglob('*.md')):
            relative = path.relative_to(ROOT)
            if relative.parts[0] == '.git':
                continue
            text = FENCE.sub('', path.read_text(encoding='utf-8'))
            for inline, reference in MARKDOWN_LINK.findall(text):
                target = (inline or reference).split('#', 1)[0]
                if not target or re.match(r'[a-z][a-z0-9+.-]*:', target, re.I):
                    continue
                checked += 1
                if not (path.parent / target).exists():
                    broken.append((relative.as_posix(), inline or reference))
        self.assertGreater(checked, 0)
        self.assertEqual(broken, [])


class TemplateOnlyContentTests(unittest.TestCase):
    def test_reference_repositories_are_named_only_where_allowed(self):
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        block = re.search(r'<!-- template-only:start -->(.*?)<!-- template-only:end -->',
                          agents, re.S)
        if block is None:
            self.skipTest('no template-only section (generated repository)')
        names = set(re.findall(r'`[\w.-]+/([\w.-]+)`', block.group(1)))
        self.assertTrue(names, 'the template-only section names no reference repository')
        outside = agents.replace(block.group(0), '')
        found = [('AGENTS.md', name) for name in sorted(names)
                 if re.search(re.escape(name), outside, re.I)]
        for path in sorted(ROOT.rglob('*')):
            relative = path.relative_to(ROOT)
            allowed = (relative.parts[0] == '.git' or '__pycache__' in relative.parts
                       or relative.parts[:2] == ('docs', 'licenses')
                       or relative.as_posix() == 'AGENTS.md')
            if allowed or not path.is_file():
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            found += [(relative.as_posix(), name) for name in sorted(names)
                      if re.search(re.escape(name), text, re.I)]
        self.assertEqual(found, [])
