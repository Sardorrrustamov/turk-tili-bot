import os
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import admin_panel as admin_panel_service
import data_loader
import keyboards
import quiz_engine
import user_stats
from config import ADMIN_ID

OPTIONS_COUNT = 4
PROMO_LINKS = [
    ("👩‍🏫 Mashhura Hoca", "https://t.me/Mashhura_hoca"),
    ("📚 Turkcha Kitoblar", "https://t.me/turkchakitoblari"),
    ("🎬 Videodarslar", "https://t.me/videodarslarbepul"),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = _is_admin_user(user.id)
    user_stats.register_user(
        user.id,
        user.first_name or "Anonim",
        user.last_name,
        user.username,
        role="admin" if is_admin else "user",
    )

    text = (
        f"Salom, *{user.first_name or 'Foydalanuvchi'}*! 🇹🇷\n\n"
        "Turkcha so'z o'rganish botiga xush kelibsiz!\n\n"
        "📚 *Testlar* — bo'lim bo'yicha test ishlash\n"
        "🗂️ *Lug'at* — tr-uz so'zlar ro'yxatini ko'rish\n"
        "🔊 *Audio* — bo'lim bo'yicha audioni tinglash\n"
        "📊 *Statistika* — natijalarni ko'rish"
    )

    await _reply(
        update,
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.home_keyboard(is_admin=is_admin),
    )
    await _send_promo(update)


async def go_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _reply(
        update,
        "🏠 Asosiy menyu",
        reply_markup=keyboards.home_keyboard(is_admin=_is_admin_user(update.effective_user.id)),
    )


async def show_test_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_levels(update, "test")


async def show_dictionary_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_levels(update, "dict")


async def show_audio_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _show_levels(update, "audio")


async def _show_levels(update: Update, mode: str):
    levels = data_loader.get_levels()
    if not levels:
        await _reply(
            update,
            "❌ Lug'at ma'lumotlari topilmadi.",
            reply_markup=keyboards.home_keyboard(is_admin=_is_admin_user(update.effective_user.id)),
        )
        return

    mode_title = {
        "test": "📚 *Test uchun darajani tanlang:*",
        "dict": "🗂️ *Lug'at uchun darajani tanlang:*",
        "audio": "🔊 *Audio uchun darajani tanlang:*",
    }[mode]

    await _reply(
        update,
        mode_title,
        parse_mode="Markdown",
        reply_markup=keyboards.levels_keyboard(mode),
    )


async def level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, mode, level = query.data.split(":", 2)
    units = data_loader.get_units_for_level(level)
    if not units:
        await query.message.edit_text(
            f"❌ {level} darajasida unitlar topilmadi.",
            reply_markup=keyboards.levels_keyboard(mode),
        )
        return

    mode_title = {
        "test": f"📚 *{level}* darajasida unit tanlang:",
        "dict": f"🗂️ *{level}* darajasida unit tanlang:",
        "audio": f"🔊 *{level}* darajasida unit tanlang:",
    }[mode]

    await query.message.edit_text(
        mode_title,
        parse_mode="Markdown",
        reply_markup=keyboards.units_keyboard(mode, level),
    )


async def unit_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, mode, level, unit = query.data.split(":", 3)
    sections = data_loader.get_sections_for_unit(level, unit)
    if not sections:
        await query.message.edit_text(
            f"❌ {unit} ichida qism topilmadi.",
            reply_markup=keyboards.units_keyboard(mode, level),
        )
        return

    mode_title = {
        "test": f"📚 *{level} - {unit}* uchun qism tanlang:",
        "dict": f"🗂️ *{level} - {unit}* uchun qism tanlang:",
        "audio": f"🔊 *{level} - {unit}* uchun qism tanlang:",
    }[mode]

    await query.message.edit_text(
        mode_title,
        parse_mode="Markdown",
        reply_markup=keyboards.sections_keyboard(mode, level, unit),
    )


async def section_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, mode, level, unit, section = query.data.split(":", 4)

    if mode == "test":
        await _start_test_from_meta(query, context, level, unit, section)
        return

    section_data = data_loader.get_section(level, unit, section)
    if not section_data:
        await query.message.edit_text(
            f"❌ {section} bo'yicha ma'lumot topilmadi.",
            reply_markup=keyboards.sections_keyboard(mode, level, unit),
        )
        return

    if mode == "dict":
        words = section_data.get("words", [])
        lines = [f"🗂️ *{level} - {unit} - {section}*", f"Jami so'zlar: *{len(words)}*", ""]
        for word in words:
            lines.append(f"• {word.get('tr', '')} - {word.get('uz', '')}")

        await query.message.edit_text(
            "\n".join(lines) if words else "❌ Bu qismda so'z topilmadi.",
            parse_mode="Markdown",
            reply_markup=keyboards.dictionary_section_actions(level, unit, section),
        )
        return

    # audio mode
    audio = section_data.get("audio")
    await query.message.edit_text(
        f"🔊 *{level} - {unit} - {section}*",
        parse_mode="Markdown",
        reply_markup=keyboards.audio_section_actions(level, unit),
    )

    if audio:
        try:
            if isinstance(audio, str) and os.path.isfile(audio):
                with open(audio, "rb") as audio_file:
                    await query.message.reply_audio(audio_file)
            else:
                await query.message.reply_audio(audio)
        except Exception:
            await query.message.reply_text("Audio hali qo‘shilmagan")
    else:
        await query.message.reply_text("Audio hali qo‘shilmagan")


async def back_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")

    if parts[1] == "levels":
        mode = parts[2]
        mode_title = {
            "test": "📚 *Test uchun darajani tanlang:*",
            "dict": "🗂️ *Lug'at uchun darajani tanlang:*",
            "audio": "🔊 *Audio uchun darajani tanlang:*",
        }[mode]
        await query.message.edit_text(
            mode_title,
            parse_mode="Markdown",
            reply_markup=keyboards.levels_keyboard(mode),
        )
        return

    if parts[1] == "units":
        mode, level = parts[2], parts[3]
        await query.message.edit_text(
            f"*{level}* darajasida unit tanlang:",
            parse_mode="Markdown",
            reply_markup=keyboards.units_keyboard(mode, level),
        )
        return

    if parts[1] == "sections":
        mode, level, unit = parts[2], parts[3], parts[4]
        await query.message.edit_text(
            f"*{level} - {unit}* uchun qism tanlang:",
            parse_mode="Markdown",
            reply_markup=keyboards.sections_keyboard(mode, level, unit),
        )


async def start_section_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, level, unit, section = query.data.split(":", 3)
    await _start_test_from_meta(query, context, level, unit, section)


async def _start_test_from_meta(query, context: ContextTypes.DEFAULT_TYPE, level: str, unit: str, section: str):
    questions = quiz_engine.build_section_quiz(level, unit, section, options_count=OPTIONS_COUNT)
    if not questions:
        await query.message.reply_text(f"❌ {section} bo'yicha test uchun so'z topilmadi.")
        return

    context.user_data["quiz_questions"] = questions
    context.user_data["quiz_meta"] = {"level": level, "unit": unit, "section": section}
    context.user_data["current_index"] = 0
    context.user_data["correct"] = 0
    context.user_data["wrong"] = 0
    context.user_data["answered"] = set()
    context.user_data["quiz_user_id"] = query.from_user.id
    context.user_data["quiz_username"] = query.from_user.username

    await query.message.reply_text(
        f"🚀 *{level} - {unit} - {section}* test boshlandi!\n"
        f"📝 Jami savollar: *{len(questions)}*",
        parse_mode="Markdown",
    )
    await _send_question(query.message, context)


async def _send_question(message, context: ContextTypes.DEFAULT_TYPE):
    questions = context.user_data.get("quiz_questions", [])
    idx = context.user_data.get("current_index", 0)

    if idx >= len(questions):
        await _send_result(message, context)
        return

    question = questions[idx]
    options = [(opt["text"], opt["is_correct"]) for opt in question["options"]]
    context.user_data[f"correct_ans_{idx}"] = question["correct"]

    await message.reply_text(
        (
            f"*{idx + 1}/{len(questions)}* ❓\n\n"
            f"🇹🇷 *{question['tr']}*\n\n"
            "O'zbekcha tarjimasini tanlang:"
        ),
        parse_mode="Markdown",
        reply_markup=keyboards.answer_keyboard(options, idx),
    )


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, q_idx, flag = query.data.split(":")
    q_idx = int(q_idx)
    is_correct = flag == "1"

    answered = context.user_data.get("answered", set())
    if q_idx in answered:
        await query.answer("Bu savolga allaqachon javob bergansiz")
        return

    answered.add(q_idx)
    context.user_data["answered"] = answered

    if is_correct:
        context.user_data["correct"] += 1
        await query.message.reply_text("✅ To'g'ri")
    else:
        context.user_data["wrong"] += 1
        correct_ans = context.user_data.get(f"correct_ans_{q_idx}", "?")
        await query.message.reply_text(f"❌ Noto'g'ri\nTo'g'ri javob: {correct_ans}")

    context.user_data["current_index"] = q_idx + 1
    await _send_question(query.message, context)


async def _send_result(message, context: ContextTypes.DEFAULT_TYPE):
    correct = context.user_data.get("correct", 0)
    wrong = context.user_data.get("wrong", 0)
    total = correct + wrong

    meta = context.user_data.get("quiz_meta", {})
    level = meta.get("level", "")
    unit = meta.get("unit", "")
    section = meta.get("section", "")

    user_id = context.user_data.get("quiz_user_id", message.chat_id)
    username = context.user_data.get("quiz_username", message.chat.username)

    user_stats.save_section_result(
        user_id=user_id,
        username=username,
        level=level,
        unit=unit,
        section=section,
        correct_answers=correct,
        wrong_answers=wrong,
    )

    percent = round((correct / total * 100) if total else 0)
    await message.reply_text(
        (
            "✅ *Test yakunlandi!*\n\n"
            f"📂 Bo'lim: *{level} - {unit} - {section}*\n"
            f"📝 Jami: *{total}*\n"
            f"✅ To'g'ri: *{correct}*\n"
            f"❌ Noto'g'ri: *{wrong}*\n"
            f"📊 Natija: *{percent}%*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboards.home_keyboard(is_admin=_is_admin_user(user_id)),
    )
    await message.reply_text(
        _promo_text(),
        parse_mode="Markdown",
        reply_markup=_promo_keyboard(),
    )

    context.user_data.pop("quiz_questions", None)
    context.user_data.pop("quiz_meta", None)
    context.user_data.pop("current_index", None)
    context.user_data.pop("correct", None)
    context.user_data.pop("wrong", None)
    context.user_data.pop("answered", None)
    context.user_data.pop("quiz_user_id", None)
    context.user_data.pop("quiz_username", None)


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = _is_admin_user(user_id)

    summary = user_stats.get_user_summary(user_id)

    sections = summary.get("sections", [])
    if not sections:
        await _reply(
            update,
            "📊 Hali test natijalari yo'q.",
            reply_markup=keyboards.home_keyboard(is_admin=is_admin),
        )
        await _send_promo(update)
        return

    lines = [
        "📊 *Sizning statistikangiz*",
        "",
    ]

    for row in sections:
        lines.append(
            (
                f"*{row['level']} - {row['unit']} - {row['section']}*\n"
                f"📝 Jami: {row['total_questions']}\n"
                f"✅ To'g'ri: {row['correct_answers']}\n"
                f"❌ Noto'g'ri: {row['wrong_answers']}\n"
                f"📅 Sana: {row['date']}"
            )
        )
        lines.append("")

    await _reply(
        update,
        "\n".join(lines).strip(),
        parse_mode="Markdown",
        reply_markup=keyboards.home_keyboard(is_admin=is_admin),
    )
    await _send_promo(update)


async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_user(update.effective_user.id):
        await _reply(
            update,
            "❌ Bu bo'lim faqat admin uchun.",
            reply_markup=keyboards.home_keyboard(is_admin=False),
        )
        return

    await _reply(
        update,
        admin_panel_service.format_users_list(),
        parse_mode="HTML",
        reply_markup=keyboards.home_keyboard(is_admin=True),
    )


async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_user(update.effective_user.id):
        await _reply(
            update,
            "❌ Bu bo'lim faqat admin uchun.",
            reply_markup=keyboards.home_keyboard(is_admin=False),
        )
        return

    await _reply(
        update,
        admin_panel_service.format_admin_dashboard(),
        parse_mode="HTML",
        reply_markup=keyboards.home_keyboard(is_admin=True),
    )


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Iltimos, menyudan kerakli bo'limni tanlang.",
        reply_markup=keyboards.home_keyboard(is_admin=_is_admin_user(update.effective_user.id)),
    )


async def _reply(
    update: Update,
    text: str,
    parse_mode: Optional[str] = None,
    reply_markup=None,
):
    if update.message:
        await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)


def _is_admin_user(user_id: int) -> bool:
    return user_stats.is_admin(user_id, ADMIN_ID)


def _promo_text() -> str:
    return (
        "📢 *Siz uchun foydali kanallar*\n\n"
        "Quyidagi sahifalarga obuna bo'ling va yangi materiallarni o'tkazib yubormang:"
    )


def _promo_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(title, url=url)] for title, url in PROMO_LINKS]
    return InlineKeyboardMarkup(buttons)


async def _send_promo(update: Update):
    if update.message:
        await update.message.reply_text(
            _promo_text(),
            parse_mode="Markdown",
            reply_markup=_promo_keyboard(),
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            _promo_text(),
            parse_mode="Markdown",
            reply_markup=_promo_keyboard(),
        )
