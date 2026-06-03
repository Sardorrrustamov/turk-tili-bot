from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import handlers
from config import BOT_TOKEN


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("home", handlers.go_home))

    app.add_handler(MessageHandler(filters.Regex(r"^📚 Testlar$"), handlers.show_test_levels))
    app.add_handler(MessageHandler(filters.Regex(r"^🗂️ Lug'at$"), handlers.show_dictionary_levels))
    app.add_handler(MessageHandler(filters.Regex(r"^🔊 Audio$"), handlers.show_audio_levels))
    app.add_handler(MessageHandler(filters.Regex(r"^📊 Statistika$"), handlers.statistics))
    app.add_handler(MessageHandler(filters.Regex(r"^👥 Foydalanuvchilar$"), handlers.user_list))
    app.add_handler(MessageHandler(filters.Regex(r"^🔧 Admin panel$"), handlers.admin_dashboard))

    app.add_handler(CallbackQueryHandler(handlers.answer_callback, pattern=r"^ans:"))
    app.add_handler(CallbackQueryHandler(handlers.start_section_test, pattern=r"^start_test:"))
    app.add_handler(CallbackQueryHandler(handlers.back_selected, pattern=r"^back:"))
    app.add_handler(CallbackQueryHandler(handlers.section_selected, pattern=r"^section:"))
    app.add_handler(CallbackQueryHandler(handlers.unit_selected, pattern=r"^unit:"))
    app.add_handler(CallbackQueryHandler(handlers.level_selected, pattern=r"^level:"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.unknown_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
