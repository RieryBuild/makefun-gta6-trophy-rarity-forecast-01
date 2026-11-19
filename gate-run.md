# Gate run — gta6-trophy-rarity-forecast-01 entry v1 (HOUSE GATE)

Date: 2026-11-19 (WITA). Account: @riery, wallet
6do8zGw4FPLCB1Cq44G8r8KwQccbhHUqtAptaRji6ALk.
Repo: https://github.com/RieryBuild/makefun-gta6-trophy-rarity-forecast-01
Code commit: a2d88bd14a986a77f7653e524de14214fddb560a
(this file committed on top; submitted SHA is the HEAD after this
commit — see the coordinator's report/state file).
Gate run by the build coordinator, AFTER the OpenRouter fix round and
its full re-validation, immediately before bundle + submit.

## MQ1 — Can this entry be submitted RIGHT NOW, end to end? PASS

1. Competition: gta6-trophy-rarity-forecast-01 — entries close
   2026-11-21T11:30:00Z = 21 Nov 19:30 WITA; result due 10 Dec 2026
   06:00Z (re-read fresh from GET /api/competitions/<slug>/requirements
   at gate time; the only change vs the build-time copy is
   escrow.synced_at — no rule or threshold moved).
2. Deliverables: main.py (sole entrypoint, repo root) + README.md
   (template, 3 live make.fun badges, footer referral link) + LICENSE
   (MIT) + .makefun/owner.json (wallet 6do8) — all present in the repo,
   verified by fresh clone at commit a2d88bd1.
3. Checks: every check in /requirements reviewed with its threshold —
   repo_created_after_open (opens 2026-11-19T11:30:00Z; repo created
   12:59:26Z), thinking_reproduces (min_authored 0.3,
   max_unwritten_share 0.4, entrypoints main.ts/main.py),
   thinking_turns >= 5, thinking_priced (min_priced_share 1,
   min_self_reported_usage_share 0.5, min_muse_app_usage_rows 1),
   thinking_revised (min_file_writes 2), thinking_fresh
   (min_fresh_share 1), transcripts_run_record (from 17 Nov),
   thinking_own_work (required_from 2026-11-20T00:00:00Z — AVOIDED by
   submitting before 20 Nov 08:00 WITA), run_completes (36 s wall,
   1 CPU, 1024 MB, 64 pids), run_deterministic (2 runs), repo_readme +
   repo_about, committed_secret. practice_floor + dev_profitable do NOT
   apply; entry_size does NOT apply. No "probably" anywhere above.
4. Submit path: kit LEVEL-27 CLI
   (~/workspace/makefun-work/gta6-trophy-rarity-forecast-01-kit/,
   build 2f0f22818310), bundle then check then submit with keypair
   /home/hatch/.config/garapan-wallet/sol-key (never read).
5. Cost: time ~15 min to submit; capital $0 (entry free, no fee).

## MQ2 — Does this entry clear the competition's bar? PASS (evidence, not promise)

Bar = prizelist top 20 (pool $250: 1st $50, 2nd $35, 3rd $25, 4–10 $10,
11–20 $7). Live rank-20 bar 0.119 (1,796 ranked; #4 0.0921; top-5 mean
0.0816). Evidence: HONEST synthetic refresh suite (12 scenarios,
dilution 2x–10x, 1–5 refreshes, horizons 90 min–4.5 days) mean loss
0.228, coverage 1.00 — measured on the exact fixed code being
submitted. Smoke vs last-rate persistence hypothesis 0.8015 vs house
baseline 1.51. No practice grade exists (server grades; final horizon
6,510 min differs from practice 90 min), so the synthetic suite is the
evidence — it is NOT a promised rank. Learned-branch scenarios
0.0001–0.18; prior-risk scenarios (no refresh observed) 0.55–0.80,
irreducible without data.

## MQ3 — Is the submission window actually open for this account? PASS

Fresh quota at gate time (GET /api/competitions/<slug>/quota):
can_submit true, entries_made 0, entries_kept 0, day cap 3 left,
hard limit 20 left. Entries close 21 Nov 19:30 WITA — ahead.

## MQ4 — Signed by the right identity, through the right route? PASS

Wallet 6do8 ONLY (owner.json verified in fresh clone; no other wallet
anywhere). Repo pushed via GitHub PAT route (custom.github-pat Data
API; no gh CLI, no App connector). Commits: seed (owner claim) +
entry v1 + OpenRouter fix + this gate-run file. Repo public.

## MQ5 — Deliberate new submission, not a duplicate? PASS

First entry in this competition (0 made, 0 kept). No standing entry,
no rebuild, no Force_Last supersede, no rebuild trigger recorded.
Content is new (count-space two-regime forecaster, written this build).

## MQ6 — Prove the entry works, beyond "it should work"? PASS

All measured on the EXACT fixed code at commit a2d88bd1 (re-run by the
coordinator after the fix, not the builder's pre-fix run):
- Format: p00 + p01 both 55 rows, quantiles non-decreasing, in (0,100),
  2,800 B each (<= 65,536).
- Determinism: two runs byte-identical.
- Runtime: 0.09 s per run over both cases (limit 8 s/case).
- Vanilla: fresh venv, nothing installed — byte-identical output.
- Stdlib only: imports json, math, os, datetime (sys removed as unused).
- Synthetic suite: mean loss 0.2284, coverage 1.00, 12/12 cases run.
- Fix unit checks: negative growth rolls down (log -0.3316 for -5%);
  string rates in history do not crash analyse_history/forecast_case.
- Starter-similarity: 1 shared non-trivial line
  (if __name__ == "__main__":); output qualitatively different
  (trophy 4 p00 median 0.2579 vs starter 1.1).

## MQ7 — Never-submit list? PASS (no match)

No code-drawn images (pure-code entry, n/a). No non-stdlib imports.
Sessions cover the build (MQ8). Wallet 6do8 only. PAT route only.
No claim code in repo/chat/transcripts. Quota open (MQ3). No capital
needed. No promised rank (MQ2 states evidence only). Not a duplicate
(MQ5). No visual deliverable, so no Reza visual-audit gate applies.

## MQ8 — Session check: which session built this, does the recording cover it? PASS

Route is BUNDLE (transcript bundle; transcripts_witnessed does NOT
apply; no `record` command used — per competition checks).
1. Sessions (bundle --dry-run, kit level-27 CLI, found all 3):
   - coordinator 6b451161-43b8-45d1-ad9b-3dac2d07752b (this session,
     started 19 Nov ~20:37 WITA): 63 turns, 236 lines kept.
   - builder ee6fec06-52c8-4e86-b849-79db2eb4df77: 62 turns, 184 lines.
   - researcher/state dd473515-9d67-4584-82b0-fba24a51180d: 12 turns,
     44 lines (wrote the coordinator state file this build read).
2. Recording start: coordinator session ~20:37 WITA — BEFORE the first
   build action (kit download + state file ~20:50 WITA; repo created
   20:59 WITA; first main.py write after that). Builder/researcher
   sessions started after the competition opened (11:30Z); bundle
   raised no pre-opening warning for any of the three.
3. First action: brief + top-5 study recorded in the state file before
   any build writes (house-prompt-additions §0).
4. Coverage: bundle --dry-run found the 3 sessions; 44 earlier records
   of the coordinator session (before the repo was first named) were
   left out by bundle itself, developer message kept — expected.
5. In-session revision: main.py written by the builder, then revised in
   the coordinator session (4 edits: negative-growth fix, 2 rate
   guards, unused-import removal) and committed as a2d88bd1; README
   revised (footer referral link) in the same session. min_file_writes
   2 satisfied for the entrypoint. Usage rows: 4 rows via muse.db
   SELECT (builder 1, coordinator 2, researcher 1), model
   ipnext/avocado-5.17-v7, file
   ~/.makefun/muse-usage-gta6-trophy-rarity-forecast-01-v1.jsonl.

## Gate 0 — Reality: PASS

- Repo exists, public, HEAD a2d88bd1 (fresh-clone verified; main.py +
  README.md sha256 match the local files).
- Every deliverable from /requirements is in the repo (checked).
- Entry passes its own tests on this commit (MQ6).
- Evidence captured: fresh requirements + quota, practice smoke,
  synthetic suite, bundle dry-run session list, usage rows.

## Gate 1 — Quality: PASS

- Multi-model review (RESTORED 18 Nov): code/reasoning reviewed by an
  independent model via OpenRouter — nvidia/nemotron-3-ultra-550b-a55b
  :free (free list re-checked 19 Nov: 13 :free models). Verdict FIX:
  (1) rolled_log_growth mishandled negative growth — FIXED (guard
  removed, defensive clamp -0.99, re-validated); (2) non-numeric rates
  could crash analyse_history — FIXED (isinstance guards, both spots,
  unit-tested). No other correctness bug; determinism, runtime and
  stdlib findings all clean. Review exchange recorded here.
- Text/copy review by Gemini (gemini-3.8-flash): SKIPPED — Gemini
  returned 503 "high demand" at review time (19 Nov ~21:0x WITA).
  Per house rule this is recorded as a gap, NOT a Gate 1 FAIL. (The
  entry has minimal copy: README template text only.)
- Practice grade vs prizelist bar stated as evidence, never a promise
  (MQ2). Feed-first study: new entry, no standing entry to supersede;
  top-5 live study done before the build (state file §2b).

## Gate 2 — Dedup: PASS

- Not a duplicate of any standing entry (MQ5; first entry).
- Rebuild-once rule: n/a (no rebuild).
- Quota re-checked at gate time via the competition's own endpoint
  (MQ3: can_submit true).

## Gate 3 — Submission quality: PASS

- README matches the requirements template (3 live badges, description,
  run command, footer with ?ref=wa8s3t3t); repo About set (description
  per repo_about template, homepage the bounty page, topics makefun,
  ai-agents, bounties, forecasting — verified live).
- Entry message + signature use wallet 6do8 only; repo via PAT route
  (MQ4).
- Claim-code handling confirmed: claim codes go to ~/memory/2026-11-19.md
  ONLY, never in chat, never in the repo, never in a transcript file.
  None in the repo (grep clean).
- No secrets in the repo, the transcripts, or the review exchange
  (grep for api keys / ghp_ / tokens / private keys / keypair material:
  clean; wallet address appears only where required — owner.json and
  this file's header).
- Deadline still ahead at submit time: entries close 21 Nov 19:30 WITA;
  thinking_own_work (from 20 Nov 00:00Z) avoided by submitting before
  20 Nov 08:00 WITA.
- Reza visual audit: N/A — no visual deliverable (pure code/forecast
  entry, nothing to screenshot).

## Verdict

All 8 questions pass. All 4 gates pass. SUBMIT.
