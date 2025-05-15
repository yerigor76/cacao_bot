from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Токен вашего бота
BOT_TOKEN = '7957459085:AAE6BGRPlvJr2fYr5DZbISVPTb1sBN545Co'
ORGANIZER_USERNAME = 'OxanaEroshenko'
REGISTERED_USERS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (
        "**ЦЕРЕМОНИЯ КАКАО В ГАМБУРГЕ**\n"
        "📅 *31 мая*  | 🕙 *10:00–15:00*  | 📍 *LovelyFit*\n\n"
        "🌿 Глубокое погружение в себя через какао, круг, мантры и движение.\n"
        "💫 Гармонизация мужского и женского начала, единение с телом и духом.\n\n"
        "🫖 Варим церемониальное какао\n"
        "🎴 Работа с МАК-картами ДО и ПОСЛЕ\n"
        "🎶 Звукотерапия: чаши, шум дождя\n"
        "👁️ Практика «Смотрим в глаза»\n"
        "🕊 Интуитивный танец в масках\n"
        "💞 Круг: счастье, отношения, дхарма\n\n"
        "🎁 Участие — *по донейшн*: сколько откликается сердцу\n"
        "📌 Мест ограничено — обязательна предварительная запись!"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Записаться", callback_data='register')],
        [InlineKeyboardButton("✉ Написать Оксане", url=f"https://t.me/{ORGANIZER_USERNAME}")]
    ]

    with open("cacao.jpg", "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'register':
        context.user_data['registering'] = True
        await query.message.reply_text("Пожалуйста, напишите ваше имя для записи на церемонию:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('registering'):
        name = update.message.text
        user = update.message.from_user
        context.user_data['registering'] = False

        REGISTERED_USERS[user.id] = {
            'name': name,
            'username': user.username,
            'tg_id': user.id
        }

        confirmation = (
            f"Спасибо, {name}! Вы записаны на церемонию 31 мая.\n"
            f"💌 Если возникнут вопросы, пишите @{ORGANIZER_USERNAME}."
        )
        await update.message.reply_text(confirmation)

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

application.run_polling()
