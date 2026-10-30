# MyTemplate

Reusable repository files and a documented GitHub settings baseline.

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
