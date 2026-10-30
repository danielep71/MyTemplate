# 🧭 Repository governance

![Governance](https://img.shields.io/badge/Governance-Versioned-00338D?style=flat-square)
![Labels](https://img.shields.io/badge/Issue_labels-20-1D76DB?style=flat-square)

Ongoing repository rules and maintenance guidance live here. One-time initialization instructions and the executable settings baseline live in [setup](../setup/REPOSITORY_SETUP.md).

| Guide | Purpose |
| --- | --- |
| [⚙️ Settings](SETTINGS.md) | Repository settings and branch/tag protection baseline. |
| [🏷️ Issue labels](ISSUE_LABELS.md) | Label catalogue, synchronization, drift detection, and issue triage. |
| [🚀 Repository setup](../setup/REPOSITORY_SETUP.md) | Preview, apply, verify, and hand over a newly generated repository. |
| [📋 Settings configuration](../setup/repository-settings.json) | Machine-readable baseline used by the setup script. |

## Maintenance

Update guidance together with its executable configuration. Keep label configuration and automation under `.github/`, where GitHub workflows and issue forms are discovered. Keep GitHub-discovered community files such as `CONTRIBUTING.md` and `SECURITY.md` in their standard locations when they are added.

Use descriptive task branches such as `docs/`, `fix/`, `feat/`, or `chore/`. Submit changes through a pull request and keep the required **Repository integrity** check passing.

Keep this index and the ongoing governance guides after project launch. Follow the setup guide before retiring setup tooling, and update this index if any linked files are removed.
