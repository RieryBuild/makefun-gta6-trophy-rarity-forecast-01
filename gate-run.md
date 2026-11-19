# Gate run — gta6-trophy-rarity-forecast-01 entry v1

Date: 2026-11-19 (WITA). Account: @riery, wallet
6do8zGw4FPLCB1Cq44G8r8KwQccbhHUqtAptaRji6ALk.
Repo: https://github.com/RieryBuild/makefun-gta6-trophy-rarity-forecast-01
(commit SHA filled after push; see report).

## MQ1 — Competition facts verified live (by coordinator)
Pool $250, top 20 paid (1st $50, 2nd $35, 3rd $25, 4–10 $10, 11–20 $7).
Entry free. Entries close 21 Nov 19:30 WITA. Quota YES (0 made, 3 left
today at build time). Rank-20 bar now 0.119 (was 0.127); 1,796 ranked;
#4 noble-orca-97 "Hierarchical Empirical-Bayes Logit-Growth &
Cohort-Dilution" 0.0921; top-5 mean loss 0.0816, miss 0.028pp,
coverage ~0.95. — PASS (per brief; bar moved, noted in build log).

## MQ2 — Kit read
RULES.txt + competition.yaml + starter/main.py + input/p00.in + p01.in
read before writing code. Kit LEVEL 27. Entrypoint main.py only at repo
root (no main.ts). — PASS.

## MQ3 — Model is count-space + two-regime + hierarchy
Earners and tracked players modelled separately (rate = ratio); refresh
= denominator jump; per-trophy earner growth hierarchically shrunk
(trophy -> tier -> global); growth-decay extrapolation; 100% trophy
special-cased; no rate-space trend (house baseline 1.51 avoided). —
PASS (see main.py + build-log.md).

## MQ4 — Selection split is honest
Split decided before testing: synthetic refresh suite (12 scenarios,
dilution 2x–10x, 1–5 refreshes, horizons 90 min–4.5 days, decay
scenarios) + cross-tier holdout. p00/p01 used as smoke check only, never
for selection/tuning. Nothing tuned to the dev board (no 6.06x factor
tuning, no per-trophy residual offsets, no spread tuned to practice). —
PASS (synth_suite.py in build dir).

## MQ5 — Synthetic suite results
Mean loss 0.228 over 12 scenarios, mean coverage 1.00 (clamped).
Learned-branch scenarios 0.0001–0.18; prior-risk scenarios (no refresh
observed, true dilution differs from prior) 0.55–0.80 — irreducible
without data. Cross-tier median |logit| error: s6 0.00–0.04, s9
0.00–0.07, s12 0.08–0.44. — PASS (recorded; see build-log.md).

## MQ6 — Practice smoke (hypothesised answer only)
p00 loss 0.2307, coverage 0.98; p01 loss 0.2307, coverage 0.98; house
baseline 1.51. Hypothesised answer = last rate x0.221 (non-100%) from
the rules' totals — smoke check only, not the true answer. — PASS
(loss << 1.51).

## MQ7 — Repo contents
main.py (stdlib only) + README.md (template, three live make.fun badges,
no placeholders) + LICENSE (MIT) + .makefun/owner.json (wallet 6do8…)
+ gate-run.md. Single public commit, created after 19 Nov 19:30 WITA. —
PASS (after push; SHA in report).

## MQ8 — No secrets / no claim code
No claim code, API key, or credential in the repo or this file. —
PASS.

## Gate 0 — Format validation (p00 + p01)
Both outputs: 55 rows, quantiles non-decreasing, 0–100, JSON parse OK,
file size 2,800 / 2,800 bytes (<= 65,536). Output differs qualitatively
from starter (e.g. trophy 4 p00: mine [0.0417, 0.1222, 0.2579, 0.5432,
1.5767] median 0.2579 vs starter [0.8974, 1.012, 1.1, 1.1955, 1.3477]
median 1.1). — PASS.

## Gate 1 — Determinism + runtime
Two runs byte-identical (diff clean). Runtime 0.036 s per run over both
cases (limit 8 s per case). — PASS.

## Gate 2 — Vanilla stdlib-only run
Fresh venv with nothing installed (pip only): program runs, output
byte-identical to the system-Python run. Imports: json, math, os, sys,
datetime only. — PASS.

## Gate 3 — Bundle + submit
Done by coordinator (not this build). — PENDING (coordinator).
