import random
from typing import Dict, List

from data_loader import get_section


def build_section_quiz(level: str, unit: str, section_name: str, options_count: int = 4) -> List[Dict]:
    section = get_section(level, unit, section_name)
    if not section:
        return []

    words = section.get("words", [])
    questions = []

    for word in words:
        question = {
            "tr": word["tr"],
            "correct": word["uz"],
            "options": _build_options(word, words, options_count),
        }
        questions.append(question)

    random.shuffle(questions)
    return questions


def _build_options(target_word: Dict[str, str], all_words: List[Dict[str, str]], options_count: int) -> List[Dict[str, object]]:
    pool = [w for w in all_words if w["tr"] != target_word["tr"]]
    wrong_count = max(0, min(options_count - 1, len(pool)))
    wrong_choices = random.sample(pool, wrong_count) if wrong_count > 0 else []

    options = [{"text": target_word["uz"], "is_correct": True}]
    for wrong_word in wrong_choices:
        options.append({"text": wrong_word["uz"], "is_correct": False})

    if len(options) < options_count:
        # Ensure minimum variants by repeating wrong answers if necessary.
        additional = [w for w in pool if w["uz"] not in {o["text"] for o in options}]
        for word in additional[: options_count - len(options)]:
            options.append({"text": word["uz"], "is_correct": False})

    random.shuffle(options)
    return options
