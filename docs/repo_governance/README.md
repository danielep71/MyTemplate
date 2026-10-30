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

## Repository controls

Settings are defined in the [settings configuration](../setup/repository-settings.json). Label configuration, issue forms, and automation live under `.github/`.

Changes follow the protected pull-request process and must pass **Repository integrity**. The [setup guide](../setup/REPOSITORY_SETUP.md) explains initialization, verification, and which files to retain after launch.

## Verification records

- [30 October 2026 — certified template snapshot](certifications/2026-10-30.md). Applies only to the identified repository and commit; generated repositories require their own verification.
