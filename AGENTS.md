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

## Template purpose

This template seeds repositories for regulatory risk calculation workbooks, such as SA-CCR, SFT, FRTB, LCR, and NSFR. Excel workbooks, exported VBA source, regulatory source copies under `docs/methodology/sources/`, the P1 definition for confirmed calculation bugs, the `traffic-history` branch, and related reserved paths are intended defaults for those repositories. Do not report them as leftovers from another project.

Generated repositories default to MPL-2.0 through the root `LICENSE`. Keep `docs/licenses/` for the files listed in its third-party notice.

## Template defaults

This repository is a template for future projects. Preserve useful policies and assumptions for file types, tooling, and reserved paths even when they are not used by this template itself. Adapt project-specific names and historical references without stripping reusable capabilities. Describe reserved paths as conventions, not as files or directories that already exist.

<!-- template-only:start -->
## Template maintenance

This section applies only to the template repository. In a repository generated from the template, delete it together with its markers; **Repository integrity** fails until you do.

- My reference repositories are `danielep71/K-SFTs` (primary) and `danielep71/K-SACCR` (secondary). Compare repository settings, issue labels, issue forms, and automation with them before changing the template.
- Port improvements in generic form. Do not copy their names, links, issue numbers, or history into template files; only this section and `docs/licenses/` may name them.
<!-- template-only:end -->
