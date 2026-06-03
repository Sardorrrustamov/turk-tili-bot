from typing import List

import user_stats


def format_users_list() -> str:
    users = user_stats.get_users_public_list()
    if not users:
        return "👥 Hozircha foydalanuvchilar topilmadi."

    lines: List[str] = ["👥 <b>Foydalanuvchilar ro'yxati</b>"]
    for idx, user in enumerate(users, start=1):
        username = user.get("username") or "username yo'q"
        lines.append(
            (
                f"\n{idx}. <b>{username}</b>\n"
                f"🆔 user_id: <code>{user['user_id']}</code>\n"
                f"🕒 first_seen: <code>{user.get('created_at', '-')}</code>\n"
                f"🔐 role: <b>{user.get('role', 'user')}</b>"
            )
        )

    return "\n".join(lines)


def format_admin_dashboard() -> str:
    activity = user_stats.get_admin_test_activity()
    if not activity:
        return "🛠 <b>Admin panel</b>\n\nHali test ishlagan foydalanuvchilar yo'q."

    lines: List[str] = ["🛠 <b>Admin panel: Test ishlagan foydalanuvchilar</b>"]
    for idx, row in enumerate(activity, start=1):
        levels = ", ".join(row["levels"]) if row["levels"] else "-"
        units = ", ".join(row["units"]) if row["units"] else "-"
        sections = "\n".join([f"   • {item}" for item in row["sections"]]) if row["sections"] else "   • -"

        lines.append(
            (
                f"\n{idx}. <b>{row['username']}</b>\n"
                f"🆔 user_id: <code>{row['user_id']}</code>\n"
                f"📚 Ishlagan qism soni: <b>{row['section_count']}</b>\n"
                f"🏷 Level: <b>{levels}</b>\n"
                f"📖 Unit: <b>{units}</b>\n"
                f"🧩 Qismlar:\n{sections}\n"
                f"✅ Jami to'g'ri javob: <b>{row['correct_answers_total']}</b>"
            )
        )

    return "\n".join(lines)
