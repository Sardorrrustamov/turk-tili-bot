import json
import os
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(__file__)
LUGAT_PATH = os.path.join(BASE_DIR, "lugat.json")


def _load_lugat() -> Dict[str, Any]:
    try:
        with open(LUGAT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def _save_lugat(data: Dict[str, Any]) -> None:
    with open(LUGAT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_levels() -> List[str]:
    data = _load_lugat()
    return list(data.keys())


def get_units_for_level(level: str) -> List[str]:
    data = _load_lugat()
    return list(data.get(level, {}).keys())


def get_sections_for_unit(level: str, unit: str) -> Dict[str, Any]:
    data = _load_lugat()
    return data.get(level, {}).get(unit, {})


def get_section(level: str, unit: str, section_name: str) -> Optional[Dict[str, Any]]:
    sections = get_sections_for_unit(level, unit)
    return sections.get(section_name)


def get_all_sections() -> List[Dict[str, Any]]:
    sections = []
    data = _load_lugat()
    for level, units in data.items():
        for unit, parts in units.items():
            for section_name, details in parts.items():
                section = {
                    "level": level,
                    "unit": unit,
                    "section": section_name,
                    "audio": details.get("audio", ""),
                    "words": details.get("words", []),
                }
                sections.append(section)
    return sections


def search_word(query: str) -> List[Dict[str, Any]]:
    q = query.strip().lower()
    results: List[Dict[str, Any]] = []
    for section in get_all_sections():
        for word in section.get("words", []):
            tr = word.get("tr", "").lower()
            uz = word.get("uz", "").lower()
            if q in tr or q in uz:
                results.append(
                    {
                        "tr": word.get("tr"),
                        "uz": word.get("uz"),
                        "level": section["level"],
                        "unit": section["unit"],
                        "section": section["section"],
                    }
                )
    return results


def add_words_to_section(
    level: str,
    unit: str,
    section_name: str,
    new_words: List[Dict[str, str]],
) -> None:
    data = _load_lugat()
    if level not in data:
        data[level] = {}
    if unit not in data[level]:
        data[level][unit] = {}
    if section_name not in data[level][unit]:
        data[level][unit][section_name] = {"audio": "", "words": []}

    existing_words = data[level][unit][section_name].get("words", [])
    existing_words.extend(new_words)
    data[level][unit][section_name]["words"] = existing_words
    _save_lugat(data)


def get_section_audio(level: str, unit: str, section_name: str) -> Optional[str]:
    section = get_section(level, unit, section_name)
    if not section:
        return None
    return section.get("audio")
