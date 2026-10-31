# MyTemplate

I use this template to start repositories for regulatory risk calculation
workbooks, such as SA-CCR, SFT, FRTB, LCR, and NSFR. It provides editing and Git
policies for Excel workbooks, exported VBA source, and byte-preserved regulatory
source copies; issue labels, issue forms, and triage automation; and a documented
GitHub settings baseline.

After creating a repository with **Use this template**, follow the
[repository setup guide](docs/setup/REPOSITORY_SETUP.md) to apply its settings.
GitHub does not inherit repository settings from templates automatically.

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply
python tools/setup_repository.py --repo OWNER/NEW-REPO --check
```

Review the [settings reference](docs/repo_governance/SETTINGS.md) and its
[JSON configuration](docs/setup/repository-settings.json). Setup requires GitHub CLI
administrative authentication and a passing integrity check on the destination.

## 🧭 Repository governance

See the [governance index](docs/repo_governance/README.md) for repository settings, issue labels, automation, and setup guidance.

## ⚖️ License

Repositories created from this template default to the [Mozilla Public License 2.0](LICENSE).
If you choose a different license for a new repository, replace `LICENSE` and keep
[`docs/licenses/`](docs/licenses/THIRD_PARTY_NOTICES.txt): the files listed there remain under MPL-2.0.
