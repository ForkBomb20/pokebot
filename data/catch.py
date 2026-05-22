from math import floor, sqrt


BALL_MULTIPLIERS = {
    "poke": 1.0,
    "great": 1.5,
    "ultra": 2.0,
    "master": 255.0,
    "net": {"default": 1.0, "bug_or_water": 3.5},
    "nest": "level_based",
    "repeat": {"default": 1.0, "registered": 3.5},
    "timer": "turn_based",
    "dive": {"default": 1.0, "water": 3.5},
    "dusk": {"default": 1.0, "dark": 3.0},
    "quick": {"default": 1.0, "first_turn": 5.0},
    "luxury": 1.0,
    "premier": 1.0,
    "heal": 1.0,
    "level": "level_compare",
    "lure": {"default": 1.0, "fishing": 4.0},
    "moon": {"default": 1.0, "moon_stone": 4.0},
    "love": {"default": 1.0, "opposite_gender": 8.0},
    "fast": {"default": 1.0, "fast_pokemon": 4.0},
    "heavy": "weight_based",
    "friend": 1.0,
    "sport": 1.5,
    "safari": 1.5,
    "dream": {"default": 1.0, "sleeping": 4.0},
    "beast": {"default": 0.1, "ultra_beast": 5.0},
}

ALL_BALLS = sorted(BALL_MULTIPLIERS.keys())

STATUS_MULTIPLIERS = {
    "none": {1: 0, 2: 0, 3: 1.0, 4: 1.0, 5: 2.5, 6: 1.0, 7: 1.0, 8: 1.0, 9: 1.0},
    "sleep": {1: 25, 2: 10, 3: 2.0, 4: 2.0, 5: 2.5, 6: 2.5, 7: 2.5, 8: 2.5, 9: 2.5},
    "freeze": {1: 25, 2: 10, 3: 2.0, 4: 2.0, 5: 2.5, 6: 2.5, 7: 2.5, 8: 2.5, 9: 2.5},
    "paralysis": {1: 12, 2: 0, 3: 1.5, 4: 1.5, 5: 1.5, 6: 1.5, 7: 1.5, 8: 1.5, 9: 1.5},
    "burn": {1: 12, 2: 0, 3: 1.5, 4: 1.5, 5: 1.5, 6: 1.5, 7: 1.5, 8: 1.5, 9: 1.5},
    "poison": {1: 12, 2: 0, 3: 1.5, 4: 1.5, 5: 1.5, 6: 1.5, 7: 1.5, 8: 1.5, 9: 1.5},
}


def get_ball_multiplier(ball: str, gen: int, level: int = 50, conditions: set = None) -> float:
    if conditions is None:
        conditions = set()

    if ball == "master":
        return 255.0

    if ball == "nest":
        if gen <= 4:
            return max((40 - level) / 10, 1.0)
        return max((41 - level) / 10, 1.0)

    if ball == "timer":
        turns = conditions.get("turns", 0) if isinstance(conditions, dict) else 10
        if gen <= 4:
            return min((turns + 10) / 10, 4.0)
        return min(1 + turns * 1229 / 4096, 4.0)

    if ball == "level":
        player_level = 50
        if level < player_level:
            ratio = player_level / level
            if ratio >= 4:
                return 8.0
            elif ratio >= 2:
                return 4.0
            else:
                return 2.0
        return 1.0

    if ball == "heavy":
        return 1.0

    entry = BALL_MULTIPLIERS.get(ball, 1.0)

    if isinstance(entry, (int, float)):
        return float(entry)

    if isinstance(entry, dict):
        if ball == "net" and "water" in conditions:
            return 3.5 if gen >= 7 else 3.0
        if ball == "net" and "bug" in conditions:
            return 3.5 if gen >= 7 else 3.0
        if ball == "repeat" and "registered" in conditions:
            return 3.5 if gen >= 7 else 3.0
        if ball == "dive" and "water" in conditions:
            return 3.5
        if ball == "dusk" and ("cave" in conditions or "night" in conditions):
            return 3.5 if gen <= 6 else 3.0
        if ball == "quick" and "first_turn" in conditions:
            return 5.0 if gen >= 5 else 4.0
        if ball == "lure" and "fishing" in conditions:
            return 4.0
        if ball == "moon" and "moon_stone" in conditions:
            return 4.0
        if ball == "love" and "opposite_gender" in conditions:
            return 8.0
        if ball == "fast" and "fast_pokemon" in conditions:
            return 4.0
        if ball == "dream" and "sleep" in conditions:
            return 4.0
        if ball == "beast" and "ultra_beast" in conditions:
            return 5.0
        return entry.get("default", 1.0)

    return 1.0


def catch_probability_gen1(catch_rate: int, hp_pct: float, ball: str, status: str) -> float:
    if ball == "master":
        return 1.0

    if ball == "great":
        ball_max = 200
        ball_divisor = 8
    elif ball == "ultra":
        ball_max = 150
        ball_divisor = 12
    else:
        ball_max = 255
        ball_divisor = 12

    status_threshold = STATUS_MULTIPLIERS.get(status, {}).get(1, 0)

    # Probability of catching via status check (step 3)
    p_status = status_threshold / ball_max if status_threshold > 0 else 0.0

    # Step 4: Check if random N - status_threshold > catch_rate
    # N is uniform in [0, ball_max-1]
    # If N < status_threshold: already caught (handled above)
    # If N - status_threshold > catch_rate: breaks free
    # So for N in [status_threshold, status_threshold + catch_rate]: passes step 4
    # Range: status_threshold to min(status_threshold + catch_rate, ball_max - 1)
    pass_step4_count = min(catch_rate, ball_max - status_threshold)
    p_pass_step4 = pass_step4_count / ball_max

    # Step 6: f calculation
    hp_current_frac = max(hp_pct / 100.0, 0.01)
    f = floor(255 * 4 / (hp_current_frac * ball_divisor))
    f = max(min(f, 255), 1)

    # Step 7: probability f >= M where M is uniform [0, 255]
    p_f = f / 256.0

    # Total: caught via status OR (pass step 4 AND pass step 7)
    p_total = p_status + (1 - p_status) * p_pass_step4 * p_f

    return min(max(p_total, 0.0), 1.0)


def catch_probability_gen2(catch_rate: int, hp_pct: float, ball: str, status: str) -> float:
    if ball == "master":
        return 1.0

    ball_mult = get_ball_multiplier(ball, 2)
    rate_modified = max(floor(catch_rate * ball_mult), 1)
    rate_modified = min(rate_modified, 255)

    hp_max = 100
    hp_current = max(floor(hp_pct), 1)

    if 3 * hp_max > 255:
        hp_max_mod = floor(floor(3 * hp_max / 2) / 2)
        hp_cur_mod = floor(floor(2 * hp_current / 2) / 2)
        if hp_cur_mod == 0:
            hp_cur_mod = 1
    else:
        hp_max_mod = 3 * hp_max
        hp_cur_mod = 2 * hp_current

    a = max(floor((hp_max_mod - hp_cur_mod) * rate_modified / hp_max_mod), 1)

    status_bonus = STATUS_MULTIPLIERS.get(status, {}).get(2, 0)
    a = min(a + status_bonus, 255)

    if a >= 255:
        return 1.0

    # Probability = a / 256 (single check against random 0-255)
    # But also need shake checks for the "capture" to stick
    # Actually in Gen II, if random [0,255] <= a, it's caught. That's the full check.
    # Shake checks only determine animation on failure.
    return (a + 1) / 256.0


def catch_probability_gen34(catch_rate: int, hp_pct: float, ball_mult: float, status_mult: float, level: int) -> float:
    if ball_mult >= 255:
        return 1.0

    hp_current_frac = max(hp_pct / 100.0, 0.01)
    hp_factor = (3.0 - 2.0 * hp_current_frac) / 3.0

    a = floor(hp_factor * catch_rate * ball_mult * status_mult)
    a = max(a, 1)

    if a >= 255:
        return 1.0

    b = floor(1048560 / floor(sqrt(floor(sqrt(floor(16711680 / a))))))

    p = (b / 65536.0) ** 4
    return min(max(p, 0.0), 1.0)


def catch_probability_gen5(catch_rate: int, hp_pct: float, ball_mult: float, status_mult: float, level: int) -> float:
    if ball_mult >= 255:
        return 1.0

    hp_current_frac = max(hp_pct / 100.0, 0.01)
    hp_factor = (3.0 - 2.0 * hp_current_frac) / 3.0

    a = floor(hp_factor * 4096 * catch_rate * ball_mult) * status_mult
    a = floor(a)
    a = max(a, 1)

    if a >= 1044480:
        return 1.0

    b = floor(65536 / (1044480 / a) ** 0.25)

    p = (b / 65536.0) ** 3
    return min(max(p, 0.0), 1.0)


def catch_probability_gen6plus(catch_rate: int, hp_pct: float, ball_mult: float, status_mult: float, level: int, gen: int) -> float:
    if ball_mult >= 255:
        return 1.0

    hp_current_frac = max(hp_pct / 100.0, 0.01)
    hp_factor = (3.0 - 2.0 * hp_current_frac) / 3.0

    a = floor(hp_factor * 4096 * catch_rate * ball_mult) * status_mult

    # Gen 8+ level bonus
    if gen >= 8 and level < 20:
        bonus_level = max((30 - level) / 10, 1.0)
        a *= bonus_level

    # Gen 9 level bonus (different formula)
    if gen >= 9 and level < 13:
        bonus_level = max((36 - 2 * level) / 10, 1.0)
        a *= bonus_level

    a = floor(a)
    a = max(a, 1)

    if a >= 1044480:
        return 1.0

    b = floor(65536 * (a / 1044480) ** 0.1875)

    p = (b / 65536.0) ** 4
    return min(max(p, 0.0), 1.0)


def calculate_catch_rate(
    catch_rate: int,
    hp_pct: float,
    ball: str,
    status: str,
    gen: int,
    level: int = 50,
    conditions: set = None,
) -> float:
    if conditions is None:
        conditions = set()

    if ball == "master":
        return 1.0

    if gen == 1:
        return catch_probability_gen1(catch_rate, hp_pct, ball, status)

    if gen == 2:
        return catch_probability_gen2(catch_rate, hp_pct, ball, status)

    ball_mult = get_ball_multiplier(ball, gen, level, conditions)
    status_mult = STATUS_MULTIPLIERS.get(status, {}).get(gen, 1.0)

    if gen <= 4:
        return catch_probability_gen34(catch_rate, hp_pct, ball_mult, status_mult, level)
    elif gen == 5:
        return catch_probability_gen5(catch_rate, hp_pct, ball_mult, status_mult, level)
    else:
        return catch_probability_gen6plus(catch_rate, hp_pct, ball_mult, status_mult, level, gen)
