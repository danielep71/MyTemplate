# MyTemplate

I use this template to start repositories for regulatory risk calculation
workbooks, such as SA-CCR, SFT, FRTB, LCR, and NSFR. It provides:

- editing and Git policies for Excel workbooks, exported VBA source, and
  byte-preserved regulatory source copies;
- issue labels, issue forms, a pull request template with a final-head review
  procedure, triage automation, and a workflow that keeps milestones on issues
  only;
- a documented GitHub settings baseline, including security features, applied
  and verified by a script that also writes a dated evidence record;
- quality gates: Ruff, strict mypy and actionlint, plus tests that hold the
  workflows to pinned actions, explicit permissions and the required check, and
  link checks: relative links and anchors on every change, external links weekly;
- a security policy, Dependabot updates for the pinned Actions and the
  hash-locked Python dependencies, and optional daily traffic collection.

After creating a repository with **Use this template**, follow the
[repository setup guide](docs/setup/REPOSITORY_SETUP.md) to apply its settings.
GitHub does not inherit repository settings from templates automatically.
First delete the template-only section of `AGENTS.md` and point the contact links in
`.github/ISSUE_TEMPLATE/config.yml` to the new repository: **Repository integrity**
fails until you do, and setup needs it to pass.

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply
python tools/setup_repository.py --repo OWNER/NEW-REPO --check \
  --report docs/repo_governance/SETTINGS_EVIDENCE.md
```

Review the [settings reference](docs/repo_governance/SETTINGS.md) and its
[JSON configuration](docs/setup/repository-settings.json). Setup requires Python 3.11+
and GitHub CLI authentication with administrator access to the destination.

## 🧭 Repository governance

See the [governance index](docs/repo_governance/README.md) for repository settings, issue labels, automation, and setup guidance.

## ⚖️ License

Repositories created from this template default to the [Mozilla Public License 2.0](LICENSE).
If you choose a different license for a new repository, replace `LICENSE` and keep
[`docs/licenses/`](docs/licenses/THIRD_PARTY_NOTICES.txt): the files listed there remain under MPL-2.0.
