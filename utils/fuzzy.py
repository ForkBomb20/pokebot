import difflib
from typing import List, Optional, Tuple

class PokemonFuzzyMatcher:
    def __init__(self, pokemon_names: List[str]):
        """
        Initialize the fuzzy matcher with a list of Pokemon names.
        
        Args:
            pokemon_names: List of correct Pokemon names
        """
        self.pokemon_names = [name.lower() for name in pokemon_names]
        self.original_names = pokemon_names
        self.name_mapping = dict(zip(self.pokemon_names, pokemon_names))
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.
        
        Args:
            s1, s2: Strings to compare
            
        Returns:
            Integer distance between strings
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def similarity_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity ratio between two strings (0-1 scale).
        
        Args:
            s1, s2: Strings to compare
            
        Returns:
            Float between 0 and 1 (1 = identical)
        """
        distance = self.levenshtein_distance(s1.lower(), s2.lower())
        max_length = max(len(s1), len(s2))
        if max_length == 0:
            return 1.0
        return (max_length - distance) / max_length
    
    def find_best_match(self, input_name: str, threshold: float = 0.7) -> Optional[str]:
        """
        Find the best matching Pokemon name.
        
        Args:
            input_name: User input (possibly with typos)
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            Best matching Pokemon name or None if no good match
        """
        input_lower = input_name.lower().strip()
        
        # First try exact match
        if input_lower in self.pokemon_names:
            return self.name_mapping[input_lower]
        
        best_match = None
        best_score = 0
        
        for pokemon_name in self.pokemon_names:
            score = self.similarity_ratio(input_lower, pokemon_name)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = pokemon_name
        
        return self.name_mapping[best_match] if best_match else None
    
    def find_multiple_matches(self, input_name: str, threshold: float = 0.6, max_results: int = 5) -> List[Tuple[str, float]]:
        """
        Find multiple potential matches with their similarity scores.
        
        Args:
            input_name: User input
            threshold: Minimum similarity threshold
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples (pokemon_name, similarity_score) sorted by score
        """
        input_lower = input_name.lower().strip()
        matches = []
        
        for pokemon_name in self.pokemon_names:
            score = self.similarity_ratio(input_lower, pokemon_name)
            if score >= threshold:
                original_name = self.name_mapping[pokemon_name]
                matches.append((original_name, score))
        
        # Sort by similarity score (descending) and return top results
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_results]
    
    def find_match_difflib(self, input_name: str, n: int = 1, cutoff: float = 0.6) -> List[str]:
        """
        Alternative method using Python's difflib for sequence matching.
        Often works well for Pokemon names.
        
        Args:
            input_name: User input
            n: Number of matches to return
            cutoff: Similarity cutoff
            
        Returns:
            List of matching Pokemon names
        """
        input_lower = input_name.lower().strip()
        matches = difflib.get_close_matches(
            input_lower, 
            self.pokemon_names, 
            n=n, 
            cutoff=cutoff
        )
        return [self.name_mapping[match] for match in matches]


# Simple function-based approach (alternative to class)
def simple_pokemon_match(input_name: str, pokemon_list: List[str], threshold: float = 0.7) -> Optional[str]:
    """
    Simple function to find the best Pokemon match.
    
    Args:
        input_name: User input
        pokemon_list: List of Pokemon names
        threshold: Similarity threshold
        
    Returns:
        Best matching Pokemon name or None
    """
    import difflib
    
    input_lower = input_name.lower().strip()
    pokemon_lower = [name.lower() for name in pokemon_list]
    
    # Try difflib first (often works well)
    matches = difflib.get_close_matches(input_lower, pokemon_lower, n=1, cutoff=threshold)
    
    if matches:
        # Find original case version
        index = pokemon_lower.index(matches[0])
        return pokemon_list[index]
    
    return None


# Example usage and testing
if __name__ == "__main__":
    # Sample Pokemon names (you'd replace this with your full list)
    pokemon_list = [
        "Pikachu", "Charizard", "Blastoise", "Venusaur", "Alakazam",
        "Machamp", "Golem", "Gengar", "Onix", "Hypno", "Electrode",
        "Exeggutor", "Hitmonlee", "Hitmonchan", "Lickitung", "Rhydon",
        "Chansey", "Tangela", "Kangaskhan", "Horsea", "Goldeen",
        "Staryu", "Mr. Mime", "Scyther", "Jynx", "Electabuzz",
        "Magmar", "Pinsir", "Tauros", "Gyarados", "Lapras", "Ditto",
        "Eevee", "Vaporeon", "Jolteon", "Flareon", "Porygon",
        "Omanyte", "Omastar", "Kabuto", "Kabutops", "Aerodactyl",
        "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini",
        "Dragonair", "Dragonite", "Mewtwo", "Mew"
    ]
    
    # Initialize the matcher
    matcher = PokemonFuzzyMatcher(pokemon_list)
    
    # Test cases
    test_inputs = [
        "pikchu",      # Missing 'a'
        "charizrd",    # Missing 'a'
        "blastois",    # Missing 'e'
        "ventosaur",   # Wrong letter
        "alacazam",    # Wrong letter
        "gyrados",     # Missing 'a'
        "snorlacs",    # Wrong ending
        "mew2",        # Different format
        "mr mime",     # Missing period
        "joltoen",      # Transposed letters
        "kangasjgan"
    ]
    
    print("=== Single Best Match ===")
    for test_input in test_inputs:
        best_match = matcher.find_best_match(test_input, threshold=0.6)
        print(f"'{test_input}' -> '{best_match}'")
    
    print("\n=== Multiple Matches ===")
    for test_input in test_inputs[:3]:  # Just show first 3
        matches = matcher.find_multiple_matches(test_input, threshold=0.5, max_results=3)
        print(f"'{test_input}':")
        for name, score in matches:
            print(f"  {name} (similarity: {score:.3f})")
        print()
    
    print("=== Using difflib method ===")
    for test_input in test_inputs[:3]:
        matches = matcher.find_match_difflib(test_input, n=3, cutoff=0.5)
        print(f"'{test_input}' -> {matches}")