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
