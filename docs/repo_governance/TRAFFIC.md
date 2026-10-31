# 📈 Repository traffic history

GitHub keeps repository traffic for 14 days. The optional **Traffic history**
workflow ([traffic-history.yml](../../.github/workflows/traffic-history.yml))
collects it once a day, with the repository's stars, forks, watchers and open
issues, and merges it into CSV files on the data-only `traffic-history`
branch, so the history outlives that window. It also writes badge files there
and opens an issue when traffic stands out (*Traffic alert* below). It is
repository analytics, not CI: it builds and tests nothing.

## 🔌 Enabling

The workflow does nothing until the repository variable `TRAFFIC_HISTORY` is
`enabled`; until then its scheduled runs are skipped. Enable it in this order:

1. **Create the branch** from a clone of the default branch:

   ```sh
   data="$(mktemp -d)/data"
   python tools/traffic_history.py init --data "$data"
   git switch --orphan traffic-history
   mv "$data" data
   git add data
   git commit -m "chore: start the traffic history"
   git push origin traffic-history
   git switch -
   ```

   `git switch --orphan` starts the branch with no files and no history in
   common with the default branch. It is never merged
   and never used as a task base. The setup baseline's **Protect traffic
   history** ruleset blocks its deletion and force pushes.
2. **Settings → Environments → New environment** `analytics`. Under
   *Deployment branches and tags*, select *Selected branches and tags* and
   allow the default branch only. Do this before adding the secret: a run that
   names a missing environment creates it without that restriction.
3. **Create the token:** a fine-grained personal access token limited to this
   repository, with repository permission **Administration: Read-only** and
   nothing else, expiring in at most 90 days. The traffic API needs that
   permission, and the workflow token cannot have it.
4. In the `analytics` environment, add the secret **TRAFFIC_TOKEN** with that
   token. Never put the token in a file, issue, comment or chat.
5. **Settings → Secrets and variables → Actions → Variables**: add the
   repository variable `TRAFFIC_HISTORY` with the value `enabled`.
6. Run **Actions → Traffic history → Run workflow** on the default branch and
   check that it passes and that `traffic-history` gains a commit.

To pause collection, delete the variable or change its value; the history
stays on the branch.

## ⏱️ Schedule

The workflow is scheduled daily at **06:17 UTC** and can be started manually
on the default branch; a manual run on any other branch is skipped. GitHub may
start scheduled runs late; each collection records the time it was actually
taken.

## 🔑 Token renewal

Before the token expires, and at least every 90 days, generate a new token
with the same settings, replace the secret, and run the workflow manually.
Revoke the token at once if it may have been exposed, or if anyone but me
changes the workflow. Collections missed while the token is invalid are lost
once they fall outside the 14-day window.

Only the fetch step receives `TRAFFIC_TOKEN`, and it runs `curl` only. The
merge script runs without it; the push uses the workflow token with
`contents: write`.

## 🗄️ Stored data

The `traffic-history` branch holds these files under `data/`:

| File | Key | Contents |
| --- | --- | --- |
| `daily.csv` | `date` | Views and unique views, clones and unique clones per UTC day. `views_collected_at` and `clones_collected_at` give the collection that last changed each pair. |
| `snapshots.csv` | `snapshot_date` | One row per collection day: the first and last day the API reported, the 14-day totals, the repository's `stars`, `forks`, `watchers` and `open_issues` at collection time, and `collected_at`, the collection that last changed that day's snapshot, referrers or paths. |
| `referrers.csv` | `snapshot_date`, `rank` | The top 10 referrers over the 14 days before each collection. |
| `paths.csv` | `snapshot_date`, `rank` | The top 10 repository paths over the same window. |
| `badges/*.json` | — | Badge files, rewritten from the stored data after each merge (*Badges* below). |

Referrers and paths are kept per collection day, because the API reports them
only as 14-day totals. `open_issues` is GitHub's count, which includes open
pull requests.

### Badges

`data/badges/` holds three files in the shields.io *endpoint* format:

| Badge | Counts |
| --- | --- |
| `clones` | Every clone in `daily.csv`, summed since tracking began. |
| `visitors (14d)` | Unique visitors over the API's 14-day window, from the latest snapshot. Daily unique counts cannot be summed into a unique count. |
| `visits` | Daily unique visitors summed since tracking began: a visitor counts once per day they visit. |

On a public repository, a README can show one with
`https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/OWNER/REPOSITORY/traffic-history/data/badges/clones.json`.
Large numbers are shortened (`1.2k`, `11k`). A badge file changes only when its
value does.

### Merge rules

`tools/traffic_history.py` merges each collection idempotently:

- **Overlapping windows:** for every date the collection reports, its values
  replace the stored ones, so a day that was incomplete when first collected
  is corrected later. Views and clones are merged separately, each with its
  own collection time.
- **Older history:** dates the collection does not report keep their values.
  Nothing is deleted.
- **No double counting:** values are replaced, never added. Unique counts are
  never summed across days or windows; a 14-day unique count exists only in
  `snapshots.csv`.
- **Same-day runs:** a collection day's snapshot, referrers and paths are one
  unit, replaced only if any of the three changed. Running the workflow twice
  with the same data changes nothing.
- **Order:** an older collection merged after a newer one, for example when a
  run is rebuilt on a newer branch tip, never replaces what the newer one
  stored; it can only fill a date or metric that nothing newer reported.

### Zero or unavailable

The API reports each day of its window, days without activity included, as
`0`. So:

- **`0`**: the day was collected and had no activity;
- **no row**: no collection covered the day, because it is before tracking
  began or because collections stopped for more than 14 days;
- **a blank metric**: one of the two series was not reported for that day.

The step summary of each run lists the dates between the first and the last
stored day that have no row.

### Visibility

The branch has the repository's visibility: on a public repository anyone can
read its CSV files. The data is aggregate (counts, referrers and paths) and
identifies no visitor. The counts include my own visits and every clone made
by CI checkouts.

## 🚨 Traffic alert

After each collection the **Traffic alert** job compares the latest snapshot
with the one before (`traffic_history.py alert`) and opens one issue, titled
`Traffic alert: <snapshot date>`, when any of these holds:

- **Views or clones spike:** the 14-day total at least doubles and grows by
  at least 100 views or 10 clones;
- **Stars or forks increase;**
- **New referrer:** a referrer never stored before brings at least 5 views.

At most one issue is opened per snapshot date: the job skips a date whose
issue exists, open or closed. The issue is assigned to the issue-form account,
labelled `P3` and `repository`, filed under the open milestone with the
earliest due date, and carries a dependency section, so it passes **Issue
triage**. The job needs at least one open milestone with a due date.

The job uses the workflow token with `issues: write` and `contents: read`. It
has no environment, so it never receives `TRAFFIC_TOKEN`, and it runs only
after a successful collection.

## 🩺 Failure diagnosis and recovery

Each run fails before anything is written if a response is missing or
invalid, and leaves the history unchanged. Read the failing step:

| Step and message | Cause | Action |
| --- | --- | --- |
| *Fetch*: `TRAFFIC_TOKEN is not set` | Secret missing, or the run is not in the `analytics` environment. | Follow *Enabling*, steps 2–4. |
| *Fetch*: HTTP 401 | Token expired or revoked. | Renew the token. |
| *Fetch*: HTTP 403 or 404 | Token lacks *Administration: read* on this repository. | Regenerate it with the settings above. |
| *Fetch*: HTTP 429 or 5xx after retries | Rate limit or GitHub outage. | Run it again later; the next run collects the same 14 days. |
| *Merge*: `ERROR: ...; the history was not changed` | The API returned an unexpected shape, or a history file no longer has the expected layout. | Inspect the response or the named file; a file edited by hand must keep its header and columns. |
| *Commit and push*: `Could not push the history` | `traffic-history` kept moving, or a rule rejected the push. | Check the branch's rules and recent commits, then run again. |
| *Check out traffic-history* fails | The branch does not exist or was deleted. | Create it as in *Enabling*, or restore it from the last known commit; never recreate it empty over existing history. |
| *Traffic alert*: `No open milestone with a due date` | Every milestone is closed, or none has a due date. | Open the next milestone with a due date, then run the workflow again. |
| *Traffic alert*: `gh issue create` fails | A label, the assignee or the milestone no longer exists. | Restore it, then run the workflow again; the history is already saved. |

A failed run can always be repeated: the merge is idempotent, and each
collection covers the last 14 days. To repair the branch, change it with a new
commit made with `python tools/traffic_history.py merge` or by hand, keeping
every header. `python tools/traffic_history.py init --data data` recreates
missing files with their headers and never overwrites an existing one.
