import os
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from tinydb import Query, TinyDB

BASE_DIR = os.path.dirname(__file__)
USERS_PATH = os.path.join(BASE_DIR, "users.json")
STATS_PATH = os.path.join(BASE_DIR, "stats.json")

users_db = TinyDB(USERS_PATH, indent=2)
stats_db = TinyDB(STATS_PATH, indent=2)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def register_user(
    user_id: int,
    first_name: str,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    role: str = "user",
) -> None:
    users_table = users_db.table("users")
    Users = Query()

    existing = users_table.get(Users.user_id == user_id)
    if existing:
        # created_at - birinchi kirgan vaqt saqlanib qoladi
        # role - mavjud admin bo'lsa tushirib yubormaymiz
        user_data = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "created_at": existing.get("created_at") or _now_utc_iso(),
            "role": existing.get("role", role),
        }
        users_table.update(user_data, Users.user_id == user_id)
        return

    users_table.insert(
        {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "created_at": _now_utc_iso(),
            "role": role,
        }
    )


def get_all_users() -> List[Dict[str, Any]]:
    users_table = users_db.table("users")
    users = users_table.all()
    Users = Query()

    for user in users:
        needs_update = False
        if not user.get("created_at"):
            user["created_at"] = _now_utc_iso()
            needs_update = True
        if not user.get("role"):
            user["role"] = "user"
            needs_update = True

        if needs_update:
            users_table.update(user, Users.user_id == user.get("user_id"))

    return sorted(users, key=lambda u: u.get("created_at", ""))


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    users_table = users_db.table("users")
    Users = Query()
    return users_table.get(Users.user_id == user_id)


def is_admin(user_id: int, admin_id: int) -> bool:
    if user_id == admin_id:
        return True

    user = get_user(user_id)
    if not user:
        return False

    return user.get("role") == "admin"


def get_users_public_list() -> List[Dict[str, Any]]:
    users = get_all_users()
    rows: List[Dict[str, Any]] = []
    for user in users:
        rows.append(
            {
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "created_at": user.get("created_at", "-"),
                "role": user.get("role", "user"),
            }
        )
    return rows


def save_section_result(
    user_id: int,
    username: Optional[str],
    level: str,
    unit: str,
    section: str,
    correct_answers: int,
    wrong_answers: int,
    result_date: Optional[str] = None,
) -> None:
    if result_date is None:
        result_date = date.today().isoformat()

    stats_table = stats_db.table("section_results")
    Stats = Query()
    query = (
        (Stats.user_id == user_id)
        & (Stats.level == level)
        & (Stats.unit == unit)
        & (Stats.section == section)
    )
    record = {
        "user_id": user_id,
        "username": username,
        "level": level,
        "unit": unit,
        "section": section,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "total_questions": correct_answers + wrong_answers,
        "date": result_date,
    }

    existing = stats_table.get(query)
    if existing:
        stats_table.update(record, query)
    else:
        stats_table.insert(record)


def get_user_stats(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    stats_table = stats_db.table("section_results")
    if user_id is None:
        rows = stats_table.all()
    else:
        Stats = Query()
        rows = stats_table.search(Stats.user_id == user_id)

    return sorted(
        rows,
        key=lambda r: (
            r.get("level", ""),
            r.get("unit", ""),
            r.get("section", ""),
            r.get("date", ""),
        ),
    )


def get_user_summary(user_id: int) -> Dict[str, Any]:
    results = get_user_stats(user_id)
    summary = {
        "user_id": user_id,
        "username": None,
        "sections": [],
        "total_questions": 0,
        "correct_answers": 0,
        "wrong_answers": 0,
    }

    user = get_user(user_id)
    if user:
        summary["username"] = user.get("username")

    for row in results:
        summary["sections"].append(
            {
                "level": row.get("level", "-"),
                "unit": row.get("unit", "-"),
                "section": row.get("section", "-"),
                "total_questions": row.get("total_questions", 0),
                "correct_answers": row.get("correct_answers", 0),
                "wrong_answers": row.get("wrong_answers", 0),
                "date": row.get("date", "-"),
            }
        )
        summary["total_questions"] += row.get("total_questions", 0)
        summary["correct_answers"] += row.get("correct_answers", 0)
        summary["wrong_answers"] += row.get("wrong_answers", 0)

    return summary


def get_admin_test_activity() -> List[Dict[str, Any]]:
    """
    Admin panel uchun: test ishlagan userlar bo'yicha agregatsiya.
    Group by user_id.
    """
    results = get_user_stats(None)
    grouped: Dict[int, Dict[str, Any]] = {}

    for row in results:
        user_id = row.get("user_id")
        if user_id is None:
            continue

        bucket = grouped.setdefault(
            user_id,
            {
                "user_id": user_id,
                "username": row.get("username"),
                "sections": set(),
                "levels": set(),
                "units": set(),
                "section_keys": [],
                "correct_answers_total": 0,
            },
        )

        level = row.get("level", "-")
        unit = row.get("unit", "-")
        section = row.get("section", "-")

        section_key = f"{level} | {unit} | {section}"
        if section_key not in bucket["sections"]:
            bucket["sections"].add(section_key)
            bucket["section_keys"].append(section_key)

        bucket["levels"].add(level)
        bucket["units"].add(f"{level} | {unit}")
        bucket["correct_answers_total"] += row.get("correct_answers", 0)

        if not bucket.get("username") and row.get("username"):
            bucket["username"] = row.get("username")

    activity_rows: List[Dict[str, Any]] = []
    for bucket in grouped.values():
        username = bucket.get("username")
        if not username:
            user = get_user(bucket["user_id"])
            username = user.get("username") if user else None

        activity_rows.append(
            {
                "user_id": bucket["user_id"],
                "username": username or "username yo'q",
                "section_count": len(bucket["sections"]),
                "levels": sorted(bucket["levels"]),
                "units": sorted(bucket["units"]),
                "sections": sorted(bucket["section_keys"]),
                "correct_answers_total": bucket["correct_answers_total"],
            }
        )

    activity_rows.sort(key=lambda x: (-x["section_count"], x["user_id"]))
    return activity_rows


def get_global_summary() -> Dict[str, Any]:
    results = get_user_stats(None)
    total_questions = sum(r.get("total_questions", 0) for r in results)
    correct_answers = sum(r.get("correct_answers", 0) for r in results)
    wrong_answers = sum(r.get("wrong_answers", 0) for r in results)
    return {
        "total_users": len(get_all_users()),
        "total_results": len(results),
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "average_percent": round((correct_answers / total_questions * 100) if total_questions else 0),
    }
