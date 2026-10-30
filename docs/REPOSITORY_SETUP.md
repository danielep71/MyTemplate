# Apply the repository settings baseline

GitHub's **Use this template** copies files, not repository settings. Run this
setup once for each new destination, after its first integrity workflow succeeds.
It does not run automatically and never provisions or stores a credential.

## Requirements

- Python 3.10 or later and a recent [GitHub CLI](https://cli.github.com/).
- Authenticate with `gh auth login --hostname github.com` using an account with
  administrator access to the destination. A fine-grained token needs repository
  Administration (write), Contents (read), and Checks (read) permissions. A normal
  Actions `GITHUB_TOKEN` cannot administer repository rulesets. Never commit tokens.
- The destination must already exist and contain the template files. Enable Actions
  and wait for `Repository integrity` to succeed on its current default-branch HEAD.
- Review that the workflow runs on every relevant PR without path filters. The
  supplied workflow runs on all branches, including a renamed default branch.
- Repository-level merge and squash methods must be enabled (normal GitHub defaults).
- Rulesets must be supported by the destination's GitHub plan and visibility.

## Commands

Run from the copied repository directory; substitute the actual destination:

```sh
# Read-only preview (default mode)
python tools/setup_repository.py --repo OWNER/NEW-REPO

# Apply missing rulesets and general settings, then read back and verify
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply

# Read-only verification; useful after setup or later configuration changes
python tools/setup_repository.py --repo OWNER/NEW-REPO --check
```

A differing existing ruleset with a managed name blocks apply before any writes.
After reviewing the preview, explicitly permit replacing the entire named ruleset:

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply --update-existing
```

Replacement removes additional rules or bypasses within that named ruleset. Rulesets
with other names and inherited organization rules remain unchanged. Duplicate managed
names are rejected. General settings are patched only when different. Repeating a
successful apply makes no writes. Preview and check never write.

The script uses explicit repository and GitHub.com arguments; it does not infer a
repository from the current directory. You may run it from another location, since
its default JSON path is relative to the script. `--config PATH` selects a reviewed
alternative baseline with the same schema.

## Coverage and verification

[repository-settings.json](repository-settings.json) is the executable counterpart
of [REPOSITORY_SETTINGS.md](REPOSITORY_SETTINGS.md): four general settings and five
active rulesets, without bypass actors. `Protect main` targets the current default
branch through `~DEFAULT_BRANCH`.

The script reads all pages, compares full rule definitions without response metadata,
creates protection before enabling automatic branch deletion, and reads back all
managed settings after changes. A successful current-HEAD check is a prerequisite,
not proof of future CI coverage or destructive enforcement testing. New rulesets are
installed with active enforcement. No branches, tags, releases or PRs are created.

Exit codes: **0** successful preview or verified match; **1** drift in `--check`;
**2** invalid configuration, missing prerequisite, inaccessible/unsupported feature,
API failure or verification failure. There is no silent skip and no success claim
for partially applied settings. API operations are not transactional: if a later
request fails, earlier changes remain. Rerun preview, resolve the reported failure,
and reapply. The script does not automatically roll back protection.

Visibility, template mode, security switches (Dependabot, CodeQL, Secret Protection),
Actions policy, Pages, secrets, environments, labels, collaborators and integrations
are outside this Markdown baseline and are not changed. Destination defaults and
inherited policies may impose additional restrictions. This is not a complete
configuration clone of the source repository.

When editing the baseline, update the JSON and Markdown together and review the
preview before applying it. Tests run without credentials or network access:

```sh
python -m unittest discover -s tests -v
```

API references: [repository updates](https://docs.github.com/en/rest/repos/repos#update-a-repository),
[rulesets](https://docs.github.com/en/rest/repos/rules),
[GitHub CLI API calls](https://cli.github.com/manual/gh_api).
