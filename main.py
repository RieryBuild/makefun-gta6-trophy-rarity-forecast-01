"""Forecast GTA VI trophy earn rates on Exophase at a future target.

Model, in one paragraph: Exophase does not update its page continuously.
It republishes the counts in bursts ("refreshes"). Between refreshes the
page is frozen; at a refresh the tracked-player count jumps (new players
syncing their profiles) and every trophy's earner count jumps by a smaller
amount (the newcomers have earned far fewer trophies than the incumbents,
except for the near-universal early trophy everyone holds). So a trophy's
rate is earners / tracked, both of which move only at refreshes, in
opposite directions. This program finds the refreshes in the case history,
measures per refresh how much the tracked count grows, how much each
trophy's earner count grows, and how often refreshes arrive, then rolls
both counts forward over the expected number of refreshes before the
target. When the history shows no refresh at all, it falls back to priors
derived from the launch-night arithmetic in the rules (tracked 638 -> 3868
in the first refresh while total trophies earned went 943 -> 4276, so the
first refresh dilutes ordinary trophies to roughly a fifth of their rate).
Uncertainty is carried on the logit scale and grows with the number of
refreshes ahead and with how small the earner count is.

Pure standard library, deterministic, no network, no randomness.
"""

import json
import math
import os
from datetime import datetime, timezone

Z_VALUES = (-1.6448536269514722, -0.6744897501960817, 0.0,
            0.6744897501960817, 1.6448536269514722)

# Priors used only when the history contains no refresh to learn from.
PRIOR_PERIOD_MIN = 270.0      # launch-night gap before the first refresh
PRIOR_TRACKED_GROWTH = 5.06   # first refresh: 638 -> 3868 tracked players
PRIOR_NEWCOMER_FRAC = 0.07    # newcomers' earn rate, as a fraction of the
                              # incumbents', for ordinary (non-universal) trophies


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def logit_pct(rate):
    # Internal logit only: the scorer clamps at 0.01, but this program's
    # own centres may legitimately fall below 0.01% after several
    # dilutions, so clamp far lower here to avoid collapsing them all
    # onto exactly 0.01.
    p = clamp(rate, 0.0001, 99.9999) / 100.0
    return math.log(p / (1.0 - p))


def inv_logit_pct(eta):
    if eta > 30.0:
        return 100.0
    if eta < -30.0:
        return 0.0
    return 100.0 / (1.0 + math.exp(-eta))


def parse_time(text):
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (ValueError, AttributeError, TypeError):
        return None


def minutes_between(a, b):
    if a is None or b is None:
        return None
    return (b - a).total_seconds() / 60.0


def median(values):
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        return None
    mid = n // 2
    if n % 2:
        return vals[mid]
    return 0.5 * (vals[mid - 1] + vals[mid])


def rolled_log_growth(growth, decay, steps):
    """Sum of log(1 + g) over `steps` refreshes when the per-refresh
    growth itself decays by `decay` each refresh (decay 1 = flat).
    A fractional final step counts proportionally."""
    if steps <= 0:
        return 0.0
    # Negative growth is real (a trophy's earners can shrink when the
    # page's 2-decimal rounding moves against a small count): log1p
    # handles it as long as growth stays above -1, which the call sites
    # enforce (per-trophy growth clamped to >= -0.9, tracked >= 0).
    # Clamp defensively anyway so a pathological value cannot blow up.
    growth = max(growth, -0.99)
    total = 0.0
    whole = int(steps)
    for j in range(whole):
        total += math.log1p(growth * (decay ** j))
    frac = steps - whole
    if frac > 0:
        total += frac * math.log1p(growth * (decay ** whole))
    return total


def shrink_toward(estimate, prior, weight):
    """Blend an estimate toward a prior; weight in [0, 1] is the prior's share."""
    return (1.0 - weight) * estimate + weight * prior


def analyse_history(case):
    """Split the history into refresh transitions and summarise them.

    Returns a dict with the last read, the list of transitions (each a
    dict of tracked growth, per-trophy earner growth and gap minutes),
    and the median refresh period in minutes (or None).
    """
    history = case.get("history") or []
    trophies = case.get("trophies") or []
    n_troph = len(trophies)
    reads = []
    for entry in history:
        rates = entry.get("rates") or []
        if len(rates) < n_troph:
            continue
        moment = parse_time(entry.get("at") or entry.get("slot") or "")
        tracked = entry.get("players_tracked")
        if not isinstance(tracked, (int, float)) or tracked <= 0:
            continue
        reads.append((moment, float(tracked), list(rates)))
    if not reads:
        return None, [], None
    transitions = []
    for prev, cur in zip(reads, reads[1:]):
        (_, n_prev, rates_prev), (moment_cur, n_cur, rates_cur) = prev, cur
        changed = abs(n_cur - n_prev) > 0.005 * n_prev
        if not changed:
            for a, b in zip(rates_prev, rates_cur):
                if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                    continue
                if abs(b - a) > 0.02:
                    changed = True
                    break
        if not changed:
            continue
        earner_growth = []
        for a, b in zip(rates_prev, rates_cur):
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                earner_growth.append(None)
                continue
            e_prev = a * n_prev / 100.0
            e_cur = b * n_cur / 100.0
            if e_prev <= 0:
                earner_growth.append(None if e_cur <= 0 else 5.0)
            else:
                earner_growth.append(e_cur / e_prev - 1.0)
        transitions.append({
            "moment": moment_cur,
            "tracked_growth": n_cur / n_prev - 1.0,
            "earner_growth": earner_growth,
        })
    # The refresh period is the time BETWEEN refreshes, i.e. between
    # successive transition moments -- not the gap between the two
    # reads that bracket one refresh (that is just the read cadence).
    moments = [t["moment"] for t in transitions if t["moment"] is not None]
    period = None
    if len(moments) >= 2:
        diffs = [minutes_between(a, b) for a, b in zip(moments, moments[1:])]
        diffs = [d for d in diffs if d is not None and d > 0]
        period = median(diffs) if diffs else None
    elif len(moments) == 1 and reads[0][0] is not None:
        period = minutes_between(reads[0][0], moments[0])
    return reads[-1], transitions, period


def newcomer_fraction(rate, median_rate):
    """Prior share of the incumbents' earn rate that newcomers hold.

    Small for rare trophies (newcomers have barely started) and graded
    by easiness: a trophy twice as common among incumbents is earned
    by newcomers roughly sqrt(2) times as often. The near-universal
    trophy everyone holds on arrival keeps a fraction near 1.
    """
    if rate >= 99.995:
        return 1.0
    base = PRIOR_NEWCOMER_FRAC * math.sqrt(max(rate, 0.05) / max(median_rate, 0.05))
    return clamp(base, 0.02, 0.95)


def forecast_case(case):
    trophies = case.get("trophies") or []
    n_troph = len(trophies)
    horizon = float(case.get("horizon_minutes") or 0.0)
    checkpoint = parse_time(case.get("at") or "")
    last, transitions, period = analyse_history(case)

    if last is None:
        # No usable history at all: flat, very uncertain forecast.
        return [{"id": t.get("id"), "q": [0.05, 0.2, 0.5, 2.0, 8.0]}
                for t in trophies]

    _, n_last, rates_last = last
    growth_decay = 1.0
    first_moment = None
    history = case.get("history") or []
    if history:
        first_moment = parse_time(history[0].get("at") or history[0].get("slot") or "")

    if transitions:
        # --- Learn everything from the observed refreshes. ---
        # Growth and cadence drift as a launch matures (early refreshes
        # are huge, later ones small), so weight the recent ones: use
        # the last three transitions for the forward rates.
        recent = transitions[-3:]
        est_period = period if period else PRIOR_PERIOD_MIN
        tracked_growth = median([t["tracked_growth"] for t in recent])
        if tracked_growth is None or tracked_growth < 0:
            tracked_growth = 0.2
        # Age of the current frozen page: time since the last refresh.
        # Walk the reads again and note when the last N-change happened;
        # the page has been frozen since that read.
        age = 0.0
        last_change_at = None
        prev_n = None
        for entry in history:
            moment = parse_time(entry.get("at") or entry.get("slot") or "")
            n_here = entry.get("players_tracked")
            if prev_n is not None and n_here != prev_n and moment is not None:
                last_change_at = moment
            prev_n = n_here
        if last_change_at is not None and checkpoint is not None:
            age = minutes_between(last_change_at, checkpoint) or 0.0
        # Expected refreshes ahead: horizon / period, plus a due-boost
        # when the page is already most of a period stale.
        k_refresh = horizon / est_period
        if est_period > 0:
            k_refresh += max(0.0, (age - 0.7 * est_period) / est_period)
        # Per-trophy earner growth per refresh, hierarchically shrunk:
        # a trophy's own reads are noisy (earner counts are small
        # integers), so blend them toward its tier's median, and the
        # tier toward the cross-trophy median. More observed refreshes
        # means more weight on the trophy's own value.
        global_growth = []
        for t in recent:
            vals = [g for g in t["earner_growth"] if g is not None]
            if vals:
                global_growth.append(median(vals))
        global_earner_growth = median(global_growth) if global_growth else 0.3
        raw_growth = []
        for i in range(n_troph):
            vals = [t["earner_growth"][i] for t in recent
                    if i < len(t["earner_growth"]) and t["earner_growth"][i] is not None]
            raw_growth.append(median(vals) if vals else None)
        tier_medians = {}
        for tier in ("platinum", "gold", "silver", "bronze"):
            vals = [raw_growth[i] for i, tr in enumerate(trophies)
                    if tr.get("tier") == tier and raw_growth[i] is not None]
            if vals:
                tier_medians[tier] = median(vals)
        per_trophy_growth = []
        for i in range(n_troph):
            tier = trophies[i].get("tier") if i < len(trophies) else None
            tier_med = tier_medians.get(tier, global_earner_growth)
            n_obs = sum(1 for t in recent
                        if i < len(t["earner_growth"]) and t["earner_growth"][i] is not None)
            if raw_growth[i] is None:
                per_trophy_growth.append(
                    (2.0 * tier_med + 1.0 * global_earner_growth) / 3.0)
            else:
                per_trophy_growth.append(
                    (n_obs * raw_growth[i] + 2.0 * tier_med
                     + 1.0 * global_earner_growth) / (n_obs + 3.0))
        tracked_growth = max(0.0, tracked_growth)
        # Saturation: if each refresh grows the tracked count by less
        # than the one before, project that decay forward instead of
        # extrapolating the recent growth flat. Same decay applies to
        # earner growth, so rates stabilise as growth fades.
        growth_decay = 1.0
        if len(transitions) >= 3:
            ratios = []
            gs = [t["tracked_growth"] for t in transitions]
            for a, b in zip(gs, gs[1:]):
                if a > 0.02:
                    ratios.append(b / a)
            if ratios:
                growth_decay = clamp(median(ratios), 0.7, 1.0)
        # How well the per-refresh move is pinned down: more observed
        # refreshes -> tighter spread on the rolled-forward move.
        move_rel_unc = 0.45 / math.sqrt(1.0 + len(transitions))
    else:
        # --- No refresh in the history: use launch-night priors. ---
        est_period = PRIOR_PERIOD_MIN
        tracked_growth = PRIOR_TRACKED_GROWTH
        # Time since the page was last refreshed is at least the span the
        # house has been watching it unchanged.
        age = minutes_between(first_moment, checkpoint) or 0.0
        # The next refresh is due once the page's age reaches the period:
        # model its arrival as uniform over the remaining window, then
        # periodic after that.
        remaining = max(0.0, est_period - age)
        if horizon <= remaining:
            k_refresh = 0.5 * horizon / max(remaining, 1.0)
        else:
            # One refresh is due inside the horizon; a second one would
            # need a full further period after it, which the horizon
            # here does not contain.
            expected_first = 0.5 * remaining
            k_refresh = 1.0 + max(0.0, horizon - expected_first - est_period) / est_period
        move_rel_unc = 0.45
        numeric_rates = sorted(r for r in rates_last
                               if isinstance(r, (int, float)) and r < 99.995)
        median_rate = median(numeric_rates) if numeric_rates else 0.78
        per_trophy_growth = []
        for rate in rates_last:
            r = rate if isinstance(rate, (int, float)) else 0.0
            per_trophy_growth.append(tracked_growth * newcomer_fraction(r, median_rate))

    log_tracked_total = rolled_log_growth(tracked_growth, growth_decay, k_refresh)
    n_target = n_last * math.exp(log_tracked_total)
    log_tracked = log_tracked_total / k_refresh if k_refresh > 0 else math.log1p(tracked_growth)

    rows = []
    for idx, trophy in enumerate(trophies):
        rate = rates_last[idx] if idx < len(rates_last) else 0.0
        if not isinstance(rate, (int, float)):
            rate = 0.0
        rate = clamp(float(rate), 0.0, 100.0)
        earners = rate * n_last / 100.0
        growth = per_trophy_growth[idx] if idx < len(per_trophy_growth) else 0.3
        growth = max(-0.9, growth)
        log_earners_total = rolled_log_growth(growth, growth_decay, k_refresh)
        earners_target = earners * math.exp(log_earners_total)
        if rate >= 99.995:
            # A trophy everyone holds stays held by everyone.
            centre = 100.0
            sigma = 0.05
        else:
            centre = 100.0 * earners_target / n_target if n_target > 0 else rate
            # Rates can fall below 0.01% after several dilutions; the
            # scorer clamps at 0.01 for the logit, but a forecast below
            # it is legal and honest, so floor at 0.001 instead.
            centre = clamp(centre, 0.001, 99.99)
            # Spread: refresh-count uncertainty scales with the size of
            # each refresh's logit move and sqrt(k), tightened when the
            # move was learned from many observed refreshes; count noise
            # scales with 1/sqrt(earners); plus a floor for model error.
            avg_log_earners = (log_earners_total / k_refresh
                               if k_refresh > 0 else math.log1p(growth))
            step = abs(avg_log_earners - log_tracked)
            sig_refresh = math.sqrt(max(k_refresh, 0.0)) * step * move_rel_unc
            # Timing risk: whether the next refresh lands inside the
            # horizon at all is a coin flip when few refreshes are
            # expected (Poisson count with mean k); its logit swing is
            # one whole refresh step, and it vanishes once k is large.
            p_event = 1.0 - math.exp(-max(k_refresh, 0.0))
            sig_timing = step * math.sqrt(p_event * (1.0 - p_event))
            sig_count = 0.8 / math.sqrt(max(earners_target, 1.0))
            sig_floor = 0.35 + 0.15 * math.sqrt(max(k_refresh, 0.0))
            sigma = math.sqrt(sig_refresh ** 2 + sig_timing ** 2
                             + sig_count ** 2 + sig_floor ** 2)
            sigma = clamp(sigma, 0.35, 1.3)
        centre_logit = logit_pct(centre) if centre < 100.0 else 9.21
        quantiles = []
        for z in Z_VALUES:
            q = inv_logit_pct(centre_logit + z * sigma)
            quantiles.append(round(clamp(q, 0.001, 100.0), 4))
        # Rounding must not break monotonicity.
        for j in range(1, 5):
            if quantiles[j] < quantiles[j - 1]:
                quantiles[j] = quantiles[j - 1]
        rows.append({"id": trophy.get("id"), "q": quantiles})
    return rows


def run():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    names = sorted(n for n in os.listdir(in_dir) if n.endswith(".in"))
    for name in names:
        case_id = name[:-3]
        with open(os.path.join(in_dir, name), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        rows = forecast_case(case)
        payload = {"trophies": rows}
        blob = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        with open(os.path.join(out_dir, case_id + ".out"), "wb") as fh:
            fh.write(blob)


if __name__ == "__main__":
    run()
