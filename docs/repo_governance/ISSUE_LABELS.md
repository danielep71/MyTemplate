# 🏷️ Issue labels & automation

![Labels](https://img.shields.io/badge/labels-20-1D76DB) ![Policy](https://img.shields.io/badge/policy-template-6F42C1)

This repository defines 20 issue labels, each with a name, description, and colour. `.github/labels.json` is authoritative; edit it through a pull request. `prune: true` removes labels outside the selected catalogue, including their issue associations.

## ⚙️ Automation

| Workflow | Purpose |
| --- | --- |
| Sync issue labels | Validates pull requests; reconciles labels after a catalogue change lands on the default branch or a manual run on the default branch. Verifies the exact live result. |
| Detect issue-label drift | Checks daily at 05:17 UTC and manually; PR runs use offline fixtures. Reports drift without modifying labels. |
| Issue triage | Audits open issues on issue events or manual runs. Reports missing assignee, priority, milestone, dependency section, invalid labels, and inconsistent blocked status. |

Only synchronization has `issues: write`. PR validation is read-only. Actions are pinned to full commit SHAs.

## 🚀 New repository

1. Enable Actions and run **Sync issue labels** from the default branch. GitHub template creation copies files; run synchronization to establish the live labels.
2. Keep template mode for the core catalogue, or set `.github/label-policy.json` to generated mode with profile `application`, `library`, or `ui-component`. Current overlays are empty, so each currently yields the same 20 labels.
3. My GitHub account, `danielep71`, is the default assignee in `tools/check_issues.py` (`OWNER`), the three issue forms (`assignees`), and corresponding test fixtures. If someone else maintains a generated repository, replace my account in all three places.
4. Create project milestones, give each open issue exactly one priority and a milestone, and assign it to me (or the account configured for a generated repository). Use `blocked` only for a named open prerequisite or `External condition:`. P1 is reserved for confirmed calculation bugs.
5. Label validation covers pull requests to every branch. Live synchronization runs only on the current default branch, including after a rename.

**Keep** the label manifests, scripts, all three workflows, issue forms, triage checker/tests, and this guide after bootstrap. They provide ongoing maintenance and must not be deleted with one-time repository setup files.

## 🎨 Catalogue

The table below lists the descriptions defined in `.github/labels.json`, which synchronization uses as its source of truth.

| Label | Colour | Description |
| --- | --- | --- |
| `behavior-change` | `#C24E00` | Intentional externally observable behavior change |
| `blocked` | `#B60205` | Cannot proceed until a named dependency is complete |
| `bug` | `#D73A4A` | Confirmed defect in behavior, correctness, error handling, or a documented contract |
| `ci` | `#24292F` | Automated quality checks, workflow maintenance, or release certification |
| `documentation` | `#0075CA` | Documentation for users or for my repository maintenance |
| `duplicate` | `#CFD3D7` | An existing issue or pull request already covers this work |
| `enhancement` | `#A2EEEF` | New capability or meaningful improvement to supported behavior |
| `good first issue` | `#7057FF` | Well-scoped task suitable for a first contribution |
| `help wanted` | `#008672` | I welcome external investigation, implementation, validation, or review |
| `invalid` | `#E4E669` | Report is incomplete, unsupported, or not actionable as submitted |
| `P1` | `#B60205` | Confirmed calculation bug: wrong results for valid inputs (reserved for this case) |
| `P2` | `#D93F0B` | Material correctness, robustness, or maintainability defect |
| `P3` | `#FBCA04` | Non-blocking quality, testing, documentation, or technical-debt improvement |
| `question` | `#D876E3` | I need further information or need to make a decision |
| `refactor` | `#6F42C1` | Internal restructuring intended to preserve supported behavior |
| `release` | `#B60276` | Release preparation, certification, evidence, packaging, or publication |
| `repository` | `#1D76DB` | Repository structure, governance, metadata, tooling, or maintenance |
| `security` | `#8B0000` | Security boundary, vulnerability handling, supply chain, or hardening |
| `tests` | `#006B75` | Regression coverage, test harnesses, fixtures, or manual validation |
| `wontfix` | `#6E7781` | I have decided not to implement or continue this work |

## Offline issue audit

Export issues in GitHub REST JSON format, then identify the repository explicitly so dependency URLs resolve correctly:

```sh
python tools/check_issues.py --input issues.json --repo-name OWNER/REPOSITORY
```

Triage uses the core labels and the profile/domain overlays selected in `.github/label-policy.json`.
