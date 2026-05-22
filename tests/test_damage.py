import pytest
from data.damage import (
    calc_stat_gen12,
    calc_stat_gen3plus,
    calc_stat,
    compute_stats,
    get_offensive_stat_name,
    get_defensive_stat_name,
    get_type_effectiveness,
    calc_damage,
    calc_damage_gen12,
    calc_damage_gen34,
    calc_damage_gen5plus,
    calculate_move_damage,
    poke_round,
)


TYPE_CHART = {
    ("fire", "grass"): 2.0,
    ("fire", "water"): 0.5,
    ("fire", "bug"): 2.0,
    ("fire", "ice"): 2.0,
    ("fire", "steel"): 2.0,
    ("fire", "rock"): 0.5,
    ("fire", "dragon"): 0.5,
    ("fire", "fire"): 0.5,
    ("water", "fire"): 2.0,
    ("water", "grass"): 0.5,
    ("water", "ground"): 2.0,
    ("water", "rock"): 2.0,
    ("water", "water"): 0.5,
    ("electric", "water"): 2.0,
    ("electric", "grass"): 0.5,
    ("electric", "ground"): 0.0,
    ("electric", "flying"): 2.0,
    ("electric", "electric"): 0.5,
    ("normal", "ghost"): 0.0,
    ("normal", "rock"): 0.5,
    ("normal", "steel"): 0.5,
    ("ground", "fire"): 2.0,
    ("ground", "electric"): 2.0,
    ("ground", "rock"): 2.0,
    ("ground", "flying"): 0.0,
    ("ice", "dragon"): 2.0,
    ("ice", "grass"): 2.0,
    ("ice", "flying"): 2.0,
    ("ice", "ground"): 2.0,
}


class TestPokeRound:
    def test_rounds_half_up(self):
        assert poke_round(10.5) == 11
        assert poke_round(10.4) == 10
        assert poke_round(10.0) == 10


class TestStatCalculation:
    def test_gen1_hp(self):
        result = calc_stat_gen12(35, 50, is_hp=True)
        assert result == 142

    def test_gen1_attack(self):
        result = calc_stat_gen12(55, 50, is_hp=False)
        assert result == 107

    def test_gen3_hp(self):
        result = calc_stat_gen3plus(35, 50, is_hp=True)
        assert result == 110

    def test_gen3_attack(self):
        result = calc_stat_gen3plus(55, 50, is_hp=False)
        assert result == 75

    def test_calc_stat_dispatches_gen1(self):
        assert calc_stat(35, 50, True, 1) == calc_stat_gen12(35, 50, True)
        assert calc_stat(35, 50, True, 2) == calc_stat_gen12(35, 50, True)

    def test_calc_stat_dispatches_gen3plus(self):
        assert calc_stat(35, 50, True, 3) == calc_stat_gen3plus(35, 50, True)
        assert calc_stat(35, 50, True, 9) == calc_stat_gen3plus(35, 50, True)

    def test_level_100_hp(self):
        result = calc_stat_gen3plus(255, 100, is_hp=True)
        assert result == 651

    def test_level_1_hp(self):
        result = calc_stat_gen3plus(35, 1, is_hp=True)
        assert result == 12

    def test_compute_stats(self):
        base_stats = [
            {"name": "hp", "value": 35},
            {"name": "attack", "value": 55},
            {"name": "defense", "value": 40},
            {"name": "special-attack", "value": 50},
            {"name": "special-defense", "value": 50},
            {"name": "speed", "value": 90},
        ]
        stats = compute_stats(base_stats, 50, 5)
        assert stats["hp"] == 110
        assert stats["speed"] == calc_stat_gen3plus(90, 50, False)


class TestPhysicalSpecialSplit:
    def test_gen1_physical_type(self):
        assert get_offensive_stat_name("normal", 1, "physical") == "attack"
        assert get_offensive_stat_name("fighting", 1, "physical") == "attack"
        assert get_offensive_stat_name("rock", 1, "physical") == "attack"

    def test_gen1_special_type(self):
        assert get_offensive_stat_name("fire", 1, "special") == "special-attack"
        assert get_offensive_stat_name("water", 1, "special") == "special-attack"
        assert get_offensive_stat_name("psychic", 1, "special") == "special-attack"

    def test_gen3_still_type_based(self):
        assert get_offensive_stat_name("fire", 3, "physical") == "special-attack"
        assert get_offensive_stat_name("rock", 3, "special") == "attack"

    def test_gen4_category_based(self):
        assert get_offensive_stat_name("fire", 4, "physical") == "attack"
        assert get_offensive_stat_name("rock", 4, "special") == "special-attack"
        assert get_offensive_stat_name("normal", 5, "special") == "special-attack"

    def test_gen1_defense_uses_special_attack(self):
        assert get_defensive_stat_name("fire", 1, "special") == "special-attack"

    def test_gen2_defense_uses_special_defense(self):
        assert get_defensive_stat_name("fire", 2, "special") == "special-defense"

    def test_gen4_defense_category_based(self):
        assert get_defensive_stat_name("fire", 4, "physical") == "defense"
        assert get_defensive_stat_name("normal", 4, "special") == "special-defense"


class TestTypeEffectiveness:
    def test_single_type(self):
        assert get_type_effectiveness("fire", ["grass"], TYPE_CHART) == 2.0
        assert get_type_effectiveness("fire", ["water"], TYPE_CHART) == 0.5
        assert get_type_effectiveness("fire", ["normal"], TYPE_CHART) == 1.0

    def test_dual_type(self):
        assert get_type_effectiveness("fire", ["grass", "bug"], TYPE_CHART) == 4.0

    def test_immune(self):
        assert get_type_effectiveness("normal", ["ghost"], TYPE_CHART) == 0.0
        assert get_type_effectiveness("electric", ["ground"], TYPE_CHART) == 0.0


class TestDamageCalcGen12:
    def test_basic_damage(self):
        min_dmg, max_dmg = calc_damage_gen12(
            level=50, power=80, attack_stat=100, defense_stat=100,
            stab=False, move_type="fire", defender_types=["normal"], type_chart=TYPE_CHART,
        )
        assert min_dmg > 0
        assert max_dmg >= min_dmg

    def test_stab(self):
        _, no_stab = calc_damage_gen12(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        _, with_stab = calc_damage_gen12(50, 80, 100, 100, True, "fire", ["normal"], TYPE_CHART)
        assert with_stab > no_stab

    def test_super_effective(self):
        _, neutral = calc_damage_gen12(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        _, se = calc_damage_gen12(50, 80, 100, 100, False, "fire", ["grass"], TYPE_CHART)
        assert se > neutral

    def test_immune(self):
        min_dmg, max_dmg = calc_damage_gen12(50, 80, 100, 100, False, "normal", ["ghost"], TYPE_CHART)
        assert min_dmg == 0
        assert max_dmg == 0


class TestDamageCalcGen34:
    def test_basic_damage(self):
        min_dmg, max_dmg = calc_damage_gen34(
            level=50, power=80, attack_stat=100, defense_stat=100,
            stab=False, move_type="fire", defender_types=["normal"], type_chart=TYPE_CHART,
        )
        assert min_dmg > 0
        assert max_dmg >= min_dmg

    def test_stab(self):
        _, no_stab = calc_damage_gen34(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        _, with_stab = calc_damage_gen34(50, 80, 100, 100, True, "fire", ["normal"], TYPE_CHART)
        assert with_stab > no_stab

    def test_immune(self):
        min_dmg, max_dmg = calc_damage_gen34(50, 80, 100, 100, False, "normal", ["ghost"], TYPE_CHART)
        assert min_dmg == 0
        assert max_dmg == 0


class TestDamageCalcGen5Plus:
    def test_basic_damage(self):
        min_dmg, max_dmg = calc_damage_gen5plus(
            level=50, power=80, attack_stat=100, defense_stat=100,
            stab=False, move_type="fire", defender_types=["normal"], type_chart=TYPE_CHART,
        )
        assert min_dmg > 0
        assert max_dmg >= min_dmg

    def test_stab(self):
        _, no_stab = calc_damage_gen5plus(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        _, with_stab = calc_damage_gen5plus(50, 80, 100, 100, True, "fire", ["normal"], TYPE_CHART)
        assert with_stab > no_stab

    def test_immune(self):
        min_dmg, max_dmg = calc_damage_gen5plus(50, 80, 100, 100, False, "normal", ["ghost"], TYPE_CHART)
        assert min_dmg == 0
        assert max_dmg == 0

    def test_4x_effective(self):
        # Fire vs Grass/Bug = 4x
        _, neutral = calc_damage_gen5plus(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        _, quad = calc_damage_gen5plus(50, 80, 100, 100, False, "fire", ["grass", "bug"], TYPE_CHART)
        assert quad > neutral * 3


class TestDamageCalcDispatch:
    def test_dispatches_gen1(self):
        result = calc_damage(50, 80, 100, 100, 1, False, "fire", ["normal"], TYPE_CHART)
        expected = calc_damage_gen12(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        assert result == expected

    def test_dispatches_gen3(self):
        result = calc_damage(50, 80, 100, 100, 3, False, "fire", ["normal"], TYPE_CHART)
        expected = calc_damage_gen34(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        assert result == expected

    def test_dispatches_gen5(self):
        result = calc_damage(50, 80, 100, 100, 5, False, "fire", ["normal"], TYPE_CHART)
        expected = calc_damage_gen5plus(50, 80, 100, 100, False, "fire", ["normal"], TYPE_CHART)
        assert result == expected

    def test_higher_attack_more_damage(self):
        _, low = calc_damage(50, 80, 80, 100, 5, False, "fire", ["normal"], TYPE_CHART)
        _, high = calc_damage(50, 80, 150, 100, 5, False, "fire", ["normal"], TYPE_CHART)
        assert high > low

    def test_higher_defense_less_damage(self):
        _, low_def = calc_damage(50, 80, 100, 80, 5, False, "fire", ["normal"], TYPE_CHART)
        _, high_def = calc_damage(50, 80, 100, 150, 5, False, "fire", ["normal"], TYPE_CHART)
        assert high_def < low_def


class TestCalculateMoveDamage:
    def setup_method(self):
        self.atk_stats = {
            "hp": 150, "attack": 100, "defense": 80,
            "special-attack": 90, "special-defense": 70, "speed": 110,
        }
        self.def_stats = {
            "hp": 160, "attack": 80, "defense": 95,
            "special-attack": 75, "special-defense": 85, "speed": 90,
        }

    def test_status_move_returns_none(self):
        move = {"name": "growl", "type": "normal", "category": "status", "power": None}
        result = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["fire"], ["grass"], 50, 5, TYPE_CHART,
        )
        assert result is None

    def test_damaging_move_returns_dict(self):
        move = {"name": "flamethrower", "type": "fire", "category": "special", "power": 90}
        result = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["fire"], ["grass"], 50, 5, TYPE_CHART,
        )
        assert result is not None
        assert result["move"] == "flamethrower"
        assert result["effectiveness"] == 2.0
        assert result["min_damage"] > 0
        assert result["min_pct"] > 0

    def test_immune_returns_zero_damage(self):
        move = {"name": "tackle", "type": "normal", "category": "physical", "power": 40}
        result = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["normal"], ["ghost"], 50, 5, TYPE_CHART,
        )
        assert result is not None
        assert result["min_damage"] == 0
        assert result["max_damage"] == 0
        assert result["effectiveness"] == 0.0

    def test_stab_applied_when_types_match(self):
        move = {"name": "flamethrower", "type": "fire", "category": "special", "power": 90}
        result_stab = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["fire"], ["normal"], 50, 5, TYPE_CHART,
        )
        result_no_stab = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["water"], ["normal"], 50, 5, TYPE_CHART,
        )
        assert result_stab["max_damage"] > result_no_stab["max_damage"]

    def test_percentage_calculation(self):
        move = {"name": "flamethrower", "type": "fire", "category": "special", "power": 90}
        result = calculate_move_damage(
            move, self.atk_stats, self.def_stats,
            ["fire"], ["normal"], 50, 5, TYPE_CHART,
        )
        expected_max_pct = result["max_damage"] / self.def_stats["hp"] * 100
        assert abs(result["max_pct"] - expected_max_pct) < 0.01


class TestKnownValues:
    """Test against values verified on calc.pokemonshowdown.com"""

    def test_gen5_thunderbolt_pikachu_vs_gyarados(self):
        # Pikachu Lv50 (0 EVs, 31 IVs, neutral) Thunderbolt vs Gyarados Lv50
        # Pikachu SpA base 50 -> stat 70
        # Gyarados HP base 95 -> 170, SpD base 100 -> 120
        atk_stat = calc_stat_gen3plus(50, 50, False)
        def_stat = calc_stat_gen3plus(100, 50, False)
        hp = calc_stat_gen3plus(95, 50, True)

        assert atk_stat == 70
        assert def_stat == 120
        assert hp == 170

        min_dmg, max_dmg = calc_damage_gen5plus(
            level=50, power=90, attack_stat=atk_stat, defense_stat=def_stat,
            stab=True, move_type="electric", defender_types=["water", "flying"],
            type_chart=TYPE_CHART,
        )
        # base = floor(floor(floor(22)*90*70/120)/50)+2 = floor(1155/50)+2 = 25
        # min: floor(25*85/100)=21 -> poke_round(21*6144/4096)=32 -> floor(32*2)=64 -> floor(64*2)=128
        # max: floor(25*100/100)=25 -> poke_round(25*6144/4096)=38 -> floor(38*2)=76 -> floor(76*2)=152
        assert min_dmg == 128
        assert max_dmg == 152
        # 75.3% - 89.4% of 170 HP (not quite an OHKO despite 4x + STAB due to Pikachu's low SpA)
        assert round(min_dmg / hp * 100, 1) == 75.3
        assert round(max_dmg / hp * 100, 1) == 89.4
