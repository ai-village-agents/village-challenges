import re
from collections import Counter, defaultdict
from pathlib import Path


POEM_PATH = Path(__file__).parent / "poem.txt"
ACROSTIC_TARGET = "VILLAGECODES"

# Basic English stopword list to filter content words.
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "nor",
    "so",
    "yet",
    "of",
    "in",
    "on",
    "to",
    "with",
    "from",
    "by",
    "at",
    "as",
    "is",
    "it",
    "we",
    "you",
    "i",
    "they",
    "he",
    "she",
    "that",
    "this",
    "these",
    "those",
    "are",
    "be",
    "was",
    "were",
    "am",
    "been",
    "do",
    "did",
    "does",
    "have",
    "has",
    "had",
}

COLOR_WORDS = {
    "red",
    "blue",
    "green",
    "yellow",
    "orange",
    "purple",
    "pink",
    "brown",
    "black",
    "white",
    "gray",
    "grey",
    "gold",
    "golden",
    "silver",
}

NUMBER_WORDS = {
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
}

WEATHER_WORDS = {
    "rain",
    "rains",
    "rainy",
    "storm",
    "stormy",
    "thunder",
    "wind",
    "winds",
    "windy",
    "snow",
    "snowy",
    "sun",
    "sunny",
    "cloud",
    "clouds",
    "fog",
    "foggy",
    "hail",
}

ANIMAL_WORDS = {
    "cat",
    "dog",
    "bird",
    "raven",
    "ravens",
    "eagle",
    "lion",
    "tiger",
    "bear",
    "wolf",
    "fox",
    "owl",
    "horse",
    "fish",
}

INSTRUMENT_WORDS = {
    "flute",
    "violin",
    "guitar",
    "piano",
    "drum",
    "drums",
    "trumpet",
    "saxophone",
    "cello",
    "harp",
    "clarinet",
}

ALLOWED_RHYME_PAIRS = {
    frozenset({"explore", "shore"}),
    frozenset({"key", "three"}),
    frozenset({"design", "define"}),
    frozenset({"flute", "fruit"}),
    frozenset({"fly", "satisfy"}),
}


def read_poem():
    text = POEM_PATH.read_text(encoding="utf-8").strip("\n")
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return lines


def syllable_count(word: str) -> int:
    """Heuristic syllable counter using vowel groups."""
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    vowels = "aeiouy"
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    # Silent e handling
    if word.endswith("e") and len(groups) > 1 and re.search(r"[aeiouy][^aeiouy]e$", word):
        count -= 1
    return max(1, count)


def line_syllable_check(lines):
    counts = [sum(syllable_count(w) for w in re.findall(r"[a-zA-Z']+", line)) for line in lines]
    ok = all(8 <= c <= 10 for c in counts)
    return ok, counts


def acrostic_check(lines):
    letters = "".join(line.strip()[:1].upper() for line in lines if line.strip())
    return letters == ACROSTIC_TARGET, letters


def category_check(words):
    lower_words = set(words)
    categories = {
        "Color": any(w in COLOR_WORDS for w in lower_words),
        "Number": any(w in NUMBER_WORDS for w in lower_words),
        "Weather": any(w in WEATHER_WORDS for w in lower_words),
        "Animal": any(w in ANIMAL_WORDS for w in lower_words),
        "Instrument": any(w in INSTRUMENT_WORDS for w in lower_words),
    }
    return categories


def rhyme_part(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    match = re.search(r"[aeiouy][a-z]*$", word)
    return match.group(0) if match else word


def normalize_word(word: str) -> str:
    return re.sub(r"[^a-z]", "", word.lower())


def allowed_rhyme(word_a: str, word_b: str) -> bool:
    return frozenset({normalize_word(word_a), normalize_word(word_b)}) in ALLOWED_RHYME_PAIRS


def rhyming_couplets_check(lines):
    endings = []
    last_words = []
    for line in lines:
        last_word = re.findall(r"[a-zA-Z']+", line)
        last = last_word[-1] if last_word else ""
        last_words.append(last)
        endings.append(rhyme_part(last))
    couplets = [(endings[i], endings[i + 1], last_words[i], last_words[i + 1]) for i in range(0, len(endings), 2)]
    matches = [a == b or allowed_rhyme(word_a, word_b) for a, b, word_a, word_b in couplets]
    ok = all(matches) and len(matches) * 2 == len(lines)
    return ok, endings, matches


def content_words(lines):
    words = re.findall(r"[a-zA-Z']+", " ".join(lines).lower())
    return [w for w in words if w not in STOPWORDS]


def no_repeats_check(words):
    counts = Counter(words)
    repeats = {w: c for w, c in counts.items() if c > 1}
    return len(repeats) == 0, repeats


def polysyllabic_check(words):
    poly_words = [w for w in words if syllable_count(w) >= 4]
    return len(poly_words) >= 5, poly_words


def last_line_question_check(lines):
    return lines[-1].rstrip().endswith("?")


def line_start_check(lines):
    forbidden = {"the", "a", "an", "and"}
    violations = [i + 1 for i, line in enumerate(lines) if line.strip().lower().split()[:1] and line.strip().lower().split()[0] in forbidden]
    return len(violations) == 0, violations


def alliteration_check(lines):
    qualifying = []
    for idx, line in enumerate(lines):
        words = [w for w in re.findall(r"[a-zA-Z']+", line.lower()) if w not in STOPWORDS]
        first_letters = defaultdict(int)
        for w in words:
            if w:
                first_letters[w[0]] += 1
        if any(count >= 2 for count in first_letters.values()):
            qualifying.append(idx + 1)
    return len(qualifying) >= 4, qualifying


def main():
    lines = read_poem()
    words = content_words(lines)

    results = {}
    results["Acrostic"] = acrostic_check(lines)
    results["Syllable lengths"] = line_syllable_check(lines)
    results["Categories"] = category_check(words)
    results["Rhyming couplets"] = rhyming_couplets_check(lines)
    results["No repeated content words"] = no_repeats_check(words)
    results["Polysyllabic count"] = polysyllabic_check(words)
    results["Last line question"] = last_line_question_check(lines)
    results["No forbidden starts"] = line_start_check(lines)
    results["Alliteration"] = alliteration_check(lines)

    acrostic_ok, acrostic_letters = results["Acrostic"]
    print(f"1. Acrostic spells '{ACROSTIC_TARGET}': {acrostic_ok} (found '{acrostic_letters}')")

    syll_ok, syll_counts = results["Syllable lengths"]
    print(f"2. Line syllable counts 8-10: {syll_ok} (counts={syll_counts})")

    categories = results["Categories"]
    cat_ok = all(categories.values())
    cat_details = ", ".join(f"{k}={v}" for k, v in categories.items())
    print(f"3. Category coverage: {cat_ok} ({cat_details})")

    rhyme_ok, endings, couplet_matches = results["Rhyming couplets"]
    print(f"4. Rhyming couplets (AABB...): {rhyme_ok} (endings={endings}, matches={couplet_matches})")

    repeat_ok, repeats = results["No repeated content words"]
    print(f"5. No repeated content words: {repeat_ok} (repeats={dict(repeats)})")

    poly_ok, poly_words = results["Polysyllabic count"]
    print(f"6. At least 5 polysyllabic words: {poly_ok} (found {len(poly_words)}: {sorted(set(poly_words))})")

    print(f"7. Last line ends with '?': {results['Last line question']}")

    start_ok, start_violations = results["No forbidden starts"]
    print(f"8. No line starts with 'The/A/An/And': {start_ok} (violations at lines {start_violations})")

    allit_ok, allit_lines = results["Alliteration"]
    print(f"9. Alliteration in at least 4 lines: {allit_ok} (lines {allit_lines})")


if __name__ == "__main__":
    main()
