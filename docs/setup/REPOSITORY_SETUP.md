<div align="center">

# 🚀 Repository Setup

**From template files to a configured GitHub repository**

[![Scope](https://img.shields.io/badge/Scope-4_settings_%C2%B7_5_rulesets-00338D?style=flat-square)](#-what-this-applies)
[![Mode](https://img.shields.io/badge/Default-Preview_only-005EB8?style=flat-square)](#-launch-sequence)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#-before-you-start)
[![Verification](https://img.shields.io/badge/Verification-Read_back_after_apply-00875A?style=flat-square)](#-verification-and-recovery)

[Prepare](#-before-you-start) · [Launch](#-launch-sequence) · [Labels](#-initialize-issue-labels) · [Coverage](#-what-this-applies) · [Clean up](#-after-launch-keep-adapt-or-remove) · [Maintain](#-maintain-the-baseline)

</div>

---

> [!IMPORTANT]
> GitHub's **Use this template** copies files, not repository settings. Run this
> setup for each new destination after its first integrity workflow succeeds.
> The script does not run automatically and never creates or stores credentials.

## 🧭 Before you start

| Prerequisite | Ready when… |
| --- | --- |
| **Runtime** | Python **3.10+** and a recent [GitHub CLI](https://cli.github.com/) are installed. |
| **Destination** | The new repository exists and contains the template files. |
| **Template cleanup** | The template-only section of `AGENTS.md`, between its `template-only` markers, is deleted. `Repository integrity` fails in a generated repository until it is. |
| **Identity** | `gh auth status --hostname github.com` shows an account with administrator access to the destination. Sign in with `gh auth login --hostname github.com`, or set `GH_TOKEN` to a fine-grained token. |
| **Token permissions** | A fine-grained token has destination repository **Administration: write**, **Contents: read**, and **Checks: read**. A workflow `GITHUB_TOKEN` cannot administer these rulesets. Never commit tokens. |
| **Integrity check** | Actions is enabled and `Repository integrity` has succeeded on the **current default-branch HEAD**. |
| **Workflow coverage** | The required job runs on every relevant PR without path filters. The supplied workflow runs on all branches, including a renamed default branch. |
| **Merge methods** | Repository-level merge commits and squash merging are enabled. |
| **Availability** | The destination's plan and visibility support repository rulesets. |

## ▶️ Launch sequence

Run from the copied repository directory. Replace `OWNER/NEW-REPO` with the
**new destination**, not the source template.

### ① Preview the changes

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO
```

Read-only by default. Review the printed destination, visibility, default branch,
and proposed API changes before applying them.

### ② Apply the baseline

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply
```

The script creates missing rulesets, patches differing general settings, and reads
back the result. Protection is installed before automatic branch deletion is enabled.

### ③ Verify the result

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO --check
```

A verified match returns **0**. Keep the output in the repository's **setup
record**: an issue, pull request, or document that holds setup evidence such as
check output, observation dates, and ruleset IDs. Running apply again against
matching settings makes no writes.

<details>
<summary><strong>⚙️ Advanced: reconcile an existing named ruleset</strong></summary>

A differing managed ruleset blocks apply before any writes. After reviewing the
preview, explicitly allow replacement of its entire definition:

```sh
python tools/setup_repository.py --repo OWNER/NEW-REPO --apply --update-existing
```

Replacement removes additional rules or bypasses inside that named ruleset.
Rulesets with other names and inherited organization rules remain unchanged.
Duplicate managed names are rejected.

The destination is always explicit; it is never inferred from the current directory.
The default JSON path is relative to the script, so it also works from another
working directory. Use `--config PATH` for a reviewed baseline with the same schema.

</details>

## 🏷️ Initialize issue labels

After creating a repository, run **Actions → Sync issue labels → Run workflow** on the default branch. This installs the 20 labels defined in this repository, including exact descriptions and colours. See [labels and automation](../repo_governance/ISSUE_LABELS.md) for triage rules and instructions for replacing my default assignee account in a generated repository. Keep the label configuration, scripts, workflows, forms, and triage tests after setup; they are ongoing automation, not bootstrap leftovers.

## 🛡️ What this applies

The [JSON configuration](repository-settings.json) is the executable counterpart
of the [settings reference](../repo_governance/SETTINGS.md).

| Layer | Managed configuration |
| --- | --- |
| **General · 4 settings** | Delete merged head branches; suggest PR branch updates; disable Projects; disable the legacy downloads flag. |
| **Protection · 5 rulesets** | Default branch, release branches, independent release-branch deletion protection, release tags, and traffic history. |
| **Enforcement** | Active rulesets with no bypass actors or ref exclusions. `Protect main` targets `~DEFAULT_BRANCH`, not a fixed branch name. |
| **Verification** | All pages are read; full rule definitions are compared without response metadata; managed settings are read back after apply. |

**Outside this baseline:** visibility, template mode, security switches (Dependabot,
CodeQL, Secret Protection), Actions policy, Pages, secrets, environments, labels,
collaborators and integrations. Configure these separately where required.
The script creates no branches, tags, releases or PRs. Destination defaults and
inherited policies may impose additional restrictions.

## 🧹 After launch: keep, adapt or remove

> [!TIP]
> **Nothing must be deleted after setup.** Keeping the script and configuration
> lets you run `--check` later and reapply an approved baseline. Removing local
> setup files does not undo settings already saved on GitHub.

### Recommended handover

| File or setting | Action in the new repository | Reason / dependency |
| --- | --- | --- |
| `AGENTS.md` | **Adapt** | Delete the template-only section first; keep the remaining instructions that still apply to the project. |
| `README.md` | **Adapt** | Replace the MyTemplate title and introduction with the project's purpose, installation and usage. Keep or replace setup links deliberately. |
| `LICENSE` | **Keep or replace** | MPL-2.0 by default. The integrity workflow requires a non-empty `LICENSE`. |
| `docs/licenses/` | **Keep** | Notice and license text for the files listed in `THIRD_PARTY_NOTICES.txt`, which remain under MPL-2.0 whatever license you choose. |
| `docs/repo_governance/SETTINGS.md` | **Keep and maintain** | Records the adopted baseline. The integrity workflow explicitly requires this file. |
| `docs/setup/repository-settings.json` | **Keep** | Enables future drift checks and reapplication. The setup tests read this file. |
| `tools/setup_repository.py` | **Keep** | Provides preview, apply and verification for future maintenance. |
| `tests/test_setup_repository.py` | **Keep while retaining setup tooling** | Imports the setup script and reads its JSON configuration. |
| `docs/setup/REPOSITORY_SETUP.md` | **Keep or retire after handover** | Optional operational guide; remove links to it if you retire it. |
| `.github/workflows/repository-integrity.yml` | **Keep and evolve** | Supplies the required `Repository integrity` check. Add project-specific checks as the project grows. |
| GitHub **Template repository** setting | **Review separately** | Choose whether the new project should itself be reusable as a template; the setup script does not change this flag. |

### Optional: retire the setup tooling

Use this route only in a **generated project** where you no longer want the setup
utilities. Keep them in the source template so future repositories receive them.

1. Run `--check` successfully and preserve the result and adopted configuration in
   the setup record.
2. Create a normal task branch and PR for cleanup. Protection remains active after
   setup; do not rely on direct pushes to the default branch.
3. In that same PR, add meaningful project checks to the workflow. Keep the job
   name **`Repository integrity`**, its coverage of all relevant PRs, the
   **Run repository tests** step, and the existing required-document and
   whitespace checks. That step also runs the label-catalogue and issue-triage
   tests in `tests/`, which stay after the setup tests are removed.
4. Remove only the retired setup files, together:

   ```text
   tools/setup_repository.py
   tests/test_setup_repository.py
   docs/setup/repository-settings.json
   docs/setup/REPOSITORY_SETUP.md
   ```

5. Update `README.md`, `docs/repo_governance/README.md`, and the **Applying this baseline** section of
   `docs/repo_governance/SETTINGS.md`: remove links and commands that reference deleted
   files, and explain how settings will be maintained going forward. Preserve the
   actual settings reference.
6. Verify that the cleanup PR reports a passing **`Repository integrity`** check
   with the intended project checks, then merge it through the protected PR process.

> [!WARNING]
> Do not delete the integrity workflow or rename its required job during cleanup.
> GitHub would continue waiting for that check and block merges. Deleting only the
> script or JSON would also break the existing setup tests. Remove individual files,
> not entire `tools/`, `tests/`, `docs/` or `.github/` directories.

Cleanup is documented as a reviewed PR because replacing template tests with useful
project validation depends on the new project. There is no automatic deletion step.

## 🔎 Verification and recovery

| Exit code | Meaning | Next action |
| --- | --- | --- |
| **0** | Successful preview, or verified match in apply/check mode | Read the mode-specific message: preview success does not mean settings were applied. |
| **1** | Drift found by `--check` | Preview the differences and decide whether to reapply. |
| **2** | Invalid configuration, missing prerequisite, unavailable feature, API failure or read-back mismatch | Resolve the reported problem, then preview and retry. |

API operations are **not transactional**. If a later request fails, earlier changes
remain. There is no silent skip, no success claim for partial application and no
automatic rollback of protection. Rerun preview to see what remains.

A passing check on the current HEAD is a prerequisite, not proof of future workflow
coverage or destructive enforcement testing. Verification covers the documented
settings, not every GitHub setting or inherited policy.

## 🔄 Maintain the baseline

Update the JSON and Markdown together when changing policy, review the preview,
and run the offline tests before applying it:

```sh
python -m unittest discover -s tests -v
```

The tests require neither credentials nor network access. Once setup tooling has
been retired from a generated project, use that project's replacement validation
and settings-maintenance process instead.

---

**References:** [Repository updates](https://docs.github.com/en/rest/repos/repos#update-a-repository)
· [Rulesets](https://docs.github.com/en/rest/repos/rules)
· [GitHub CLI API](https://cli.github.com/manual/gh_api)

[↑ Back to top](#-repository-setup)
