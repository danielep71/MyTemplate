# 🔎 Pull request review

Every change reaches a protected branch through a pull request that passes
**Repository integrity**, the required check. This guide covers the evidence I
record before merging: which commit was reviewed, by what, and what was not.
The pull request template has a *Final-head review* section for it.

## ✅ Final-head review

A review covers only the commit it read. When Codex reviews pull requests in
this repository, it runs when a pull request is opened or a draft is marked
ready, not after later pushes. Before merging a pull request I authored:

1. Push the last fixes and note the current head commit SHA.
2. Once any earlier review has finished, post `@codex review` as a new
   top-level comment on the pull request.
3. Wait until the Codex review summary shows **Completed** for that head SHA.
   A running review, a reaction, or a completed review of an older commit is
   not enough. If the summary shows a shortened SHA, open the commit and
   compare it with the head.
4. Fix or answer every finding and resolve the threads that apply. Any further
   push, a branch update included, makes the review stale: repeat from step 1.
5. Check that **Repository integrity** passes on the current head and that
   GitHub's merge requirements are met. Record the reviewed SHA, the review
   link and the check result in the pull request, then merge.

If the review fails, is unavailable or does not finish, I leave the pull
request open and record what blocks it.

## ⚖️ Recorded exceptions

Record these in the *Final-head review* section, in place of the steps above:

- **Identical reviewed content.** A pull request whose head has the same tree
  as a commit already reviewed against the same base may cite that review.
  Record both SHAs and the shared tree, and do not claim a review of the head
  itself.
- **Merge authorized without a final-head review.** I may decide to merge
  without one. Record my decision word for word, what changed after the last
  reviewed commit, and that no review of the final head is claimed.
- **Bot pull requests.** Codex does not review pull requests opened by
  Dependabot or another bot. Record my own review of the final diff and head
  SHA, with **Repository integrity** passing, and do not claim a Codex review.

Self-review, an automated review and CI are separate kinds of evidence. This
procedure is a merge rule I apply, not an additional required status check.
