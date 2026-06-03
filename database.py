from tinydb import TinyDB, Query
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "words.json")
STATS_PATH = os.path.join(os.path.dirname(__file__), "stats.json")
USERS_PATH = os.path.join(os.path.dirname(__file__), "users.json")
DB_JSON_PATH = os.path.join(os.path.dirname(__file__), "db.json")

db = TinyDB(DB_PATH, indent=2)
stats_db = TinyDB(STATS_PATH, indent=2)
users_db = TinyDB(USERS_PATH, indent=2)

# ─────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────


def _init_db():
    """Agar DB bo'sh bo'lsa default so'zlarni yukla"""
    sections_table = db.table("sections")
    if len(sections_table) == 0:
        for section_name, words in DEFAULT_SECTIONS.items():
            sections_table.insert({"name": section_name, "words": words})


_init_db()


def get_all_sections():
    try:
        with open(DB_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sections = []
        for level, units in data.items():
            for unit_name, parts in units.items():
                words = []
                for part_name, word_list in parts.items():
                    words.extend(word_list)
                sections.append({"name": unit_name, "level": level, "parts": parts, "words": words})
        return sections
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def get_levels():
    try:
        with open(DB_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return list(data.keys())
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def get_units_for_level(level: str):
    try:
        with open(DB_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return list(data.get(level, {}).keys())
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def get_parts_for_unit(level: str, unit: str):
    try:
        with open(DB_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(level, {}).get(unit, {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def get_section_by_name(name: str):
    sections = get_all_sections()
    for section in sections:
        if section["name"] == name:
            return section
    return None


def get_all_users():
    users_table = users_db.table("users")
    return users_table.all()


def register_user(user_id: int, first_name: str, last_name: str = None, username: str = None):
    users_table = users_db.table("users")
    Users = Query()
    existing = users_table.get(Users.user_id == user_id)
    user_data = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }
    if existing:
        users_table.update(user_data, Users.user_id == user_id)
    else:
        users_table.insert(user_data)


def get_user_stats(user_id: int = None):
    stats_table = stats_db.table("results")
    if user_id is None:
        return stats_table.all()
    Stats = Query()
    return stats_table.search(Stats.user_id == user_id)


def get_all_words():
    words = []
    for section in get_all_sections():
        words.extend(section.get("words", []))
    return words


def get_letters():
    letters = sorted(
        {w["tr"][0].upper() for w in get_all_words() if w.get("tr")}
    )
    return letters


def get_words_by_letter(letter: str):
    return sorted(
        [w for w in get_all_words() if w.get("tr", "").strip().lower().startswith(letter.lower())],
        key=lambda item: item["tr"].lower(),
    )


def find_word(query: str):
    q = query.strip().lower()
    results = []
    for item in get_all_words():
        tr = item.get("tr", "").lower()
        uz = item.get("uz", "").lower()
        if q == tr or q == uz or q in tr or q in uz:
            results.append(item)
    return results


def add_section(name: str, words: list):
    sections_table = db.table("sections")
    Section = Query()
    existing = sections_table.search(Section.name == name)
    if existing:
        # Mavjud bo'limga so'z qo'sh
        current_words = existing[0]["words"]
        current_words.extend(words)
        sections_table.update({"words": current_words}, Section.name == name)
    else:
        sections_table.insert({"name": name, "words": words})


def add_words_to_section(section_name: str, new_words: list):
    sections_table = db.table("sections")
    Section = Query()
    existing = sections_table.search(Section.name == section_name)
    if existing:
        words = existing[0]["words"]
        words.extend(new_words)
        sections_table.update({"words": words}, Section.name == section_name)
    else:
        sections_table.insert({"name": section_name, "words": new_words})


# ─── Statistika ───────────────────────────────
def save_stats(user_id: int, section_name: str, correct: int, total: int):
    stats_table = stats_db.table("results")
    stats_table.insert({
        "user_id": user_id,
        "section": section_name,
        "correct": correct,
        "total": total,
    })


def get_user_stats(user_id: int):
    stats_table = stats_db.table("results")
    Stats = Query()
    return stats_table.search(Stats.user_id == user_id)
