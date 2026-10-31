# Repository instructions

## Documentation voice

- Write my decisions and responsibilities in first person: “I”, “me”, and “my”.
- Do not describe me in third person as “the maintainer” or “the owner”.
- Address instructions for contributors and template users directly to the reader.

## Repository scope

- Describe this repository's current files, configuration, and behavior.
- Do not insert references to other repositories, copied-from history, unrelated projects, or conversation context into operational documentation.
- Make reusable guidance self-contained so it remains accurate in newly generated repositories.
- Keep necessary platform/dependency documentation links and third-party license notices. Put licensing attribution in dedicated license files, not operational guides.
- Do not invent project history, capabilities, or dependencies.

## Branch names

Use descriptive prefixes such as `docs/`, `fix/`, `feat/`, or `chore/`. Do not use `codex/` or `claude/`.

## Audience separation

Keep editorial rules, assistant instructions, branch-naming preferences, and collaboration conventions in this file. Reader-facing documentation must explain the repository and its usage, not our writing process. Apply the requested voice naturally; do not explain that prose is written “in my voice”.

## Domain defaults

This repository holds, or provides the starting point for, a regulatory risk calculation workbook such as SA-CCR, SFT, FRTB, LCR, or NSFR. Excel workbooks, exported VBA source, regulatory source copies under `docs/methodology/sources/`, the P1 definition for confirmed calculation bugs, the `traffic-history` branch, and related reserved paths are intended defaults. Do not report them as leftovers from another project.

The repository is licensed under MPL-2.0 through the root `LICENSE` unless that file says otherwise. Keep `docs/licenses/` for the files listed in its third-party notice.

## Reusable defaults

Preserve useful policies and assumptions for file types, tooling, and reserved paths even when this repository does not use them yet. Adapt project-specific names and historical references without stripping reusable capabilities. Describe reserved paths as conventions, not as files or directories that already exist.

<!-- template-only:start -->
## Template maintenance

This section applies only to the template repository. In a repository generated from the template, delete it together with its markers; **Repository integrity** fails until you do.

- This repository is the template that new workbook repositories are created from. Keep its files generic: each one must still be correct after it is copied into a new repository.
- My reference repositories are `danielep71/K-SFTs` (primary) and `danielep71/K-SACCR` (secondary). Compare repository settings, issue labels, issue forms, and automation with them before changing the template.
- My other workbook repositories, `danielep71/K-FRTB-SA`, `danielep71/K-LCR`, and `danielep71/K-NSFR`, are also compared: adopt what they do better, and report where they lag behind the template.
- Port improvements in generic form. Do not copy their names, links, issue numbers, or history into template files; only this section and `docs/licenses/` may name them.
- This repository has no issues or milestones, so the rule that links each bot pull request to a tracking issue applies only in generated repositories. Here, merge a Dependabot pull request once **Repository integrity** passes.
- From a session on this repository, change only this repository. Read the reference repositories and any other repository only to compare them; for changes they need, write a message for a session dedicated to that repository instead of committing, pushing, or posting there.
<!-- template-only:end -->
