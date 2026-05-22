import pytest
from data.catch import (
    calculate_catch_rate,
    catch_probability_gen1,
    catch_probability_gen2,
    catch_probability_gen34,
    catch_probability_gen5,
    catch_probability_gen6plus,
    get_ball_multiplier,
)


class TestBallMultipliers:
    def test_basic_balls(self):
        assert get_ball_multiplier("poke", 5) == 1.0
        assert get_ball_multiplier("great", 5) == 1.5
        assert get_ball_multiplier("ultra", 5) == 2.0

    def test_nest_ball_low_level(self):
        assert get_ball_multiplier("nest", 5, level=5) > 1.0
        assert get_ball_multiplier("nest", 5, level=40) == 1.0

    def test_dusk_ball_conditions(self):
        assert get_ball_multiplier("dusk", 5, conditions=set()) == 1.0
        assert get_ball_multiplier("dusk", 5, conditions={"night"}) == 3.5
        assert get_ball_multiplier("dusk", 7, conditions={"night"}) == 3.0
        assert get_ball_multiplier("dusk", 5, conditions={"cave"}) == 3.5

    def test_quick_ball(self):
        assert get_ball_multiplier("quick", 5, conditions={"first_turn"}) == 5.0
        assert get_ball_multiplier("quick", 4, conditions={"first_turn"}) == 4.0
        assert get_ball_multiplier("quick", 5, conditions=set()) == 1.0

    def test_net_ball(self):
        assert get_ball_multiplier("net", 7, conditions={"water"}) == 3.5
        assert get_ball_multiplier("net", 4, conditions={"water"}) == 3.0
        assert get_ball_multiplier("net", 5, conditions=set()) == 1.0


class TestGen1:
    def test_master_ball(self):
        assert catch_probability_gen1(3, 100, "master", "none") == 1.0

    def test_full_hp_no_status(self):
        # Mewtwo (catch rate 3) at full HP with Poke Ball - very low
        prob = catch_probability_gen1(3, 100, "poke", "none")
        assert 0 < prob < 0.05

    def test_low_hp_sleep(self):
        # Should be much higher with sleep and low HP
        prob = catch_probability_gen1(3, 1, "ultra", "sleep")
        assert prob > catch_probability_gen1(3, 100, "ultra", "none")

    def test_high_catch_rate_easy(self):
        # Magikarp (catch rate 255) should be very easy
        prob = catch_probability_gen1(255, 50, "poke", "none")
        assert prob > 0.5


class TestGen2:
    def test_master_ball(self):
        assert catch_probability_gen2(3, 100, "master", "none") == 1.0

    def test_sleep_adds_bonus(self):
        prob_none = catch_probability_gen2(45, 50, "ultra", "none")
        prob_sleep = catch_probability_gen2(45, 50, "ultra", "sleep")
        assert prob_sleep > prob_none

    def test_paralysis_no_bonus(self):
        # Gen 2 bug: paralysis gives no bonus
        prob_none = catch_probability_gen2(45, 50, "ultra", "none")
        prob_para = catch_probability_gen2(45, 50, "ultra", "paralysis")
        assert prob_para == prob_none

    def test_low_hp_better(self):
        prob_full = catch_probability_gen2(45, 100, "poke", "none")
        prob_low = catch_probability_gen2(45, 1, "poke", "none")
        assert prob_low > prob_full


class TestGen34:
    def test_master_ball(self):
        assert catch_probability_gen34(3, 100, 255.0, 1.0, 50) == 1.0

    def test_guaranteed_at_255(self):
        # catch_rate 255 at 1HP with ultra ball and sleep
        prob = catch_probability_gen34(255, 1, 2.0, 2.0, 50)
        assert prob == 1.0

    def test_mewtwo_full_hp(self):
        # Mewtwo (rate 3) at full HP, Ultra Ball, no status
        prob = catch_probability_gen34(3, 100, 2.0, 1.0, 50)
        assert 0 < prob < 0.05

    def test_sleep_helps(self):
        prob_none = catch_probability_gen34(45, 50, 2.0, 1.0, 50)
        prob_sleep = catch_probability_gen34(45, 50, 2.0, 2.0, 50)
        assert prob_sleep > prob_none

    def test_low_hp_helps(self):
        prob_full = catch_probability_gen34(45, 100, 2.0, 1.0, 50)
        prob_low = catch_probability_gen34(45, 10, 2.0, 1.0, 50)
        assert prob_low > prob_full


class TestGen5:
    def test_master_ball(self):
        assert catch_probability_gen5(3, 100, 255.0, 1.0, 50) == 1.0

    def test_higher_status_mult(self):
        # Gen 5 uses 2.5 for sleep instead of 2.0
        prob_sleep = catch_probability_gen5(45, 50, 2.0, 2.5, 50)
        prob_para = catch_probability_gen5(45, 50, 2.0, 1.5, 50)
        assert prob_sleep > prob_para

    def test_low_hp_helps(self):
        prob_full = catch_probability_gen5(45, 100, 2.0, 1.0, 50)
        prob_low = catch_probability_gen5(45, 10, 2.0, 1.0, 50)
        assert prob_low > prob_full


class TestGen6Plus:
    def test_master_ball(self):
        assert catch_probability_gen6plus(3, 100, 255.0, 1.0, 50, 6) == 1.0

    def test_level_bonus_gen8(self):
        # Level bonus kicks in for level < 20 in gen 8
        prob_high = catch_probability_gen6plus(45, 50, 2.0, 1.0, 50, 8)
        prob_low_level = catch_probability_gen6plus(45, 50, 2.0, 1.0, 5, 8)
        assert prob_low_level > prob_high

    def test_no_level_bonus_gen6(self):
        # No level bonus in gen 6
        prob_high = catch_probability_gen6plus(45, 50, 2.0, 1.0, 50, 6)
        prob_low_level = catch_probability_gen6plus(45, 50, 2.0, 1.0, 5, 6)
        assert prob_low_level == prob_high


class TestCalculateCatchRate:
    def test_dispatches_gen1(self):
        prob = calculate_catch_rate(45, 50.0, "ultra", "sleep", 1)
        assert 0 < prob <= 1

    def test_dispatches_gen4(self):
        prob = calculate_catch_rate(45, 50.0, "ultra", "sleep", 4)
        assert 0 < prob <= 1

    def test_dispatches_gen9(self):
        prob = calculate_catch_rate(45, 50.0, "ultra", "sleep", 9)
        assert 0 < prob <= 1

    def test_master_ball_all_gens(self):
        for gen in range(1, 10):
            assert calculate_catch_rate(3, 100.0, "master", "none", gen) == 1.0

    def test_conditions_passed(self):
        prob_no_cond = calculate_catch_rate(45, 50.0, "dusk", "none", 5, conditions=set())
        prob_night = calculate_catch_rate(45, 50.0, "dusk", "none", 5, conditions={"night"})
        assert prob_night > prob_no_cond
