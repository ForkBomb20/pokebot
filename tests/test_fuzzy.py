import pytest
from utils.fuzzy import PokemonFuzzyMatcher, simple_pokemon_match


@pytest.fixture
def matcher():
    names = [
        "Pikachu", "Charizard", "Blastoise", "Venusaur", "Alakazam",
        "Machamp", "Gengar", "Gyarados", "Snorlax", "Dragonite",
        "Mr. Mime", "Porygon-Z", "Ho-Oh", "Deoxys-attack", "Farfetch’d",
        "Type: Null", "Tapu Koko", "Nidoran♀", "Nidoran♂",
    ]
    return PokemonFuzzyMatcher(names)


class TestLevenshteinDistance:
    def test_identical_strings(self, matcher):
        assert matcher.levenshtein_distance("pikachu", "pikachu") == 0

    def test_single_insertion(self, matcher):
        assert matcher.levenshtein_distance("pikchu", "pikachu") == 1

    def test_single_deletion(self, matcher):
        assert matcher.levenshtein_distance("pikachuu", "pikachu") == 1

    def test_single_substitution(self, matcher):
        assert matcher.levenshtein_distance("pikacha", "pikachu") == 1

    def test_empty_string(self, matcher):
        assert matcher.levenshtein_distance("", "pikachu") == 7

    def test_both_empty(self, matcher):
        assert matcher.levenshtein_distance("", "") == 0

    def test_completely_different(self, matcher):
        assert matcher.levenshtein_distance("abc", "xyz") == 3

    def test_symmetric(self, matcher):
        assert matcher.levenshtein_distance("hello", "world") == matcher.levenshtein_distance("world", "hello")


class TestSimilarityRatio:
    def test_identical(self, matcher):
        assert matcher.similarity_ratio("pikachu", "pikachu") == 1.0

    def test_completely_different(self, matcher):
        assert matcher.similarity_ratio("abc", "xyz") == 0.0

    def test_empty_strings(self, matcher):
        assert matcher.similarity_ratio("", "") == 1.0

    def test_one_char_off(self, matcher):
        ratio = matcher.similarity_ratio("pikachu", "pikachx")
        assert 0.8 < ratio < 1.0

    def test_case_insensitive(self, matcher):
        assert matcher.similarity_ratio("PIKACHU", "pikachu") == 1.0


class TestFindBestMatch:
    def test_exact_match(self, matcher):
        assert matcher.find_best_match("Pikachu") == "Pikachu"

    def test_exact_match_case_insensitive(self, matcher):
        assert matcher.find_best_match("pikachu") == "Pikachu"

    def test_exact_match_with_whitespace(self, matcher):
        assert matcher.find_best_match("  pikachu  ") == "Pikachu"

    def test_typo_missing_letter(self, matcher):
        assert matcher.find_best_match("pikchu") == "Pikachu"

    def test_typo_wrong_letter(self, matcher):
        assert matcher.find_best_match("charizrd") == "Charizard"

    def test_typo_extra_letter(self, matcher):
        assert matcher.find_best_match("blastoisse") == "Blastoise"

    def test_no_match_below_threshold(self, matcher):
        assert matcher.find_best_match("xyzxyzxyz", threshold=0.7) is None

    def test_high_threshold_rejects_poor_match(self, matcher):
        assert matcher.find_best_match("pika", threshold=0.9) is None

    def test_low_threshold_accepts_poor_match(self, matcher):
        result = matcher.find_best_match("pika", threshold=0.4)
        assert result is not None

    def test_special_characters_mr_mime(self, matcher):
        assert matcher.find_best_match("mr. mime") == "Mr. Mime"

    def test_special_characters_farfetchd(self, matcher):
        assert matcher.find_best_match("farfetch’d") == "Farfetch’d"

    def test_hyphenated_name(self, matcher):
        assert matcher.find_best_match("porygon-z") == "Porygon-Z"

    def test_alternate_form(self, matcher):
        assert matcher.find_best_match("deoxys-attack") == "Deoxys-attack"


class TestFindMultipleMatches:
    def test_returns_list(self, matcher):
        results = matcher.find_multiple_matches("pika", threshold=0.4)
        assert isinstance(results, list)

    def test_results_are_tuples(self, matcher):
        results = matcher.find_multiple_matches("pika", threshold=0.4)
        if results:
            assert isinstance(results[0], tuple)
            assert len(results[0]) == 2

    def test_sorted_by_score_descending(self, matcher):
        results = matcher.find_multiple_matches("dragon", threshold=0.4)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_max_results_limit(self, matcher):
        results = matcher.find_multiple_matches("a", threshold=0.1, max_results=3)
        assert len(results) <= 3

    def test_no_matches_returns_empty(self, matcher):
        results = matcher.find_multiple_matches("zzzzzzzzzzz", threshold=0.9)
        assert results == []

    def test_exact_match_has_score_1(self, matcher):
        results = matcher.find_multiple_matches("pikachu", threshold=0.9)
        assert any(name == "Pikachu" and score == 1.0 for name, score in results)


class TestFindMatchDifflib:
    def test_finds_close_match(self, matcher):
        results = matcher.find_match_difflib("pikchu", n=1, cutoff=0.6)
        assert "Pikachu" in results

    def test_respects_n_parameter(self, matcher):
        results = matcher.find_match_difflib("dragon", n=3, cutoff=0.4)
        assert len(results) <= 3

    def test_no_match_returns_empty(self, matcher):
        results = matcher.find_match_difflib("xyzxyzxyz", n=1, cutoff=0.9)
        assert results == []


class TestSimplePokemonMatch:
    def test_finds_match(self):
        names = ["Pikachu", "Charizard", "Blastoise"]
        assert simple_pokemon_match("pikchu", names, threshold=0.6) == "Pikachu"

    def test_no_match(self):
        names = ["Pikachu", "Charizard", "Blastoise"]
        assert simple_pokemon_match("xyzxyz", names, threshold=0.9) is None

    def test_exact_match(self):
        names = ["Pikachu", "Charizard", "Blastoise"]
        assert simple_pokemon_match("pikachu", names, threshold=0.7) == "Pikachu"
