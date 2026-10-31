"""Cross-file contracts for the template's public label catalogue."""

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CatalogueDocumentationTests(unittest.TestCase):
    def test_guide_matches_core_names_colors_and_descriptions(self):
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        guide = (ROOT / 'docs/repo_governance/ISSUE_LABELS.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| `([^`]+)` \| `#([0-9A-F]+)` \| (.+) \|$', guide, re.M)
        expected = [(label['name'], label['color'], label['description'])
                    for label in manifest['core']]
        self.assertEqual(rows, expected)

    def test_documented_label_counts_match_the_template_selection(self):
        manifest = json.loads((ROOT / '.github/labels.json').read_text(encoding='utf-8'))
        expected = str(len(manifest['core']))
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
