from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

import data_loader


def home_keyboard(is_admin: bool = False):
    buttons = [
        [KeyboardButton("📚 Testlar"), KeyboardButton("🗂️ Lug'at"), KeyboardButton("🔊 Audio")],
        [KeyboardButton("📊 Statistika")],
    ]
    if is_admin:
        buttons.append([KeyboardButton("👥 Foydalanuvchilar"), KeyboardButton("🔧 Admin panel")])

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def levels_keyboard(mode: str) -> InlineKeyboardMarkup:
    levels = data_loader.get_levels()
    btns = []
    row = []
    for level in levels:
        row.append(InlineKeyboardButton(level, callback_data=f"level:{mode}:{level}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    if row:
        btns.append(row)

    return InlineKeyboardMarkup(btns)


def units_keyboard(mode: str, level: str) -> InlineKeyboardMarkup:
    units = data_loader.get_units_for_level(level)
    btns = []
    row = []
    for unit in units:
        row.append(InlineKeyboardButton(unit, callback_data=f"unit:{mode}:{level}:{unit}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    if row:
        btns.append(row)

    btns.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"back:levels:{mode}")])
    return InlineKeyboardMarkup(btns)


def sections_keyboard(mode: str, level: str, unit: str) -> InlineKeyboardMarkup:
    parts = data_loader.get_sections_for_unit(level, unit)
    btns = []
    for part_name, part_data in parts.items():
        word_count = len(part_data.get("words", []))
        btns.append(
            [
                InlineKeyboardButton(
                    f"{part_name} ({word_count})",
                    callback_data=f"section:{mode}:{level}:{unit}:{part_name}",
                )
            ]
        )

    btns.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"back:units:{mode}:{level}")])
    return InlineKeyboardMarkup(btns)


def dictionary_section_actions(level: str, unit: str, section: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Test ishlash", callback_data=f"start_test:{level}:{unit}:{section}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data=f"back:sections:dict:{level}:{unit}")],
        ]
    )


def audio_section_actions(level: str, unit: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Orqaga", callback_data=f"back:sections:audio:{level}:{unit}")]]
    )


def answer_keyboard(options: list, q_index: int):
    btns = []
    row = []
    for text, is_correct in options:
        flag = "1" if is_correct else "0"
        row.append(InlineKeyboardButton(text, callback_data=f"ans:{q_index}:{flag}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    if row:
        btns.append(row)
    return InlineKeyboardMarkup(btns)
