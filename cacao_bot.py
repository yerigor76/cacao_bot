import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))         # для /settext и /broadcast
ORGANIZER_ID = 1558696819                     # Telegram ID Оксаны (получатель регистрации)
ORGANIZER_USERNAME = 'OxanaEroshenko'

user_text = "Добро пожаловать! ✨ Церемония какао ждёт вас."
REGISTERED_USERS = {}
SUBSCRIBERS = set()

# Шаги регистрации по очереди
REGISTRATION_STEP = {
    "name": "Пожалуйста, введите ваше имя:",
    "surname": "Введите вашу фамилию:",
    "payment": "Выберите способ оплаты:",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUBSCRIBERS.add(update.effective_chat.id)

    keyboard = [
        [InlineKeyboardButton("✅ Записаться", callback_data='register')],
        [InlineKeyboardButton("✉ Написать Оксане", url=f"https://t.me/{ORGANIZER_USERNAME}")]
    ]

    try:
        with open("cacao.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=user_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await update.message.reply_text(user_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'register':
        context.user_data['step'] = 'name'
        await query.message.reply_text(REGISTRATION_STEP['name'])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('step')

    if step == 'name':
        context.user_data['name'] = update.message.text
        context.user_data['step'] = 'surname'
        await update.message.reply_text(REGISTRATION_STEP['surname'])

    elif step == 'surname':
        context.user_data['surname'] = update.message.text
        context.user_data['step'] = 'payment'
        keyboard = [
            [
                InlineKeyboardButton("💶 Наличные", callback_data='pay_cash'),
                InlineKeyboardButton("💳 Карта", callback_data='pay_card')
            ]
        ]
        await update.message.reply_text(REGISTRATION_STEP['payment'],
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    elif step is None:
        await update.message.reply_text("Нажмите кнопку «Записаться», чтобы начать регистрацию.")

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payment_method = "Наличные" if query.data == 'pay_cash' else "Карта"
    context.user_data['payment'] = payment_method
    context.user_data['step'] = None

    name = context.user_data.get('name', '')
    surname = context.user_data.get('surname', '')
    payment = context.user_data.get('payment', '')

    confirmation = (
        f"🎉 Спасибо за регистрацию, {name}!\n"
        f"Фамилия: {surname}\n"
        f"Оплата: {payment}\n\n"
        f"До встречи на церемонии! ✨"
    )
    await query.message.reply_text(confirmation)

    # Отправка данных Оксане
    message_to_organizer = (
        f"📝 Новая регистрация:\n"
        f"Имя: {name}\n"
        f"Фамилия: {surname}\n"
        f"Оплата: {payment}\n"
        f"Telegram: @{update.effective_user.username or 'нет username'}"
    )
    try:
        await context.bot.send_message(chat_id=ORGANIZER_ID, text=message_to_organizer)
    except:
        print("❗ Не удалось отправить сообщение организатору.")

async def settext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет прав на изменение текста.")
        return
    global user_text
    user_text = " ".join(context.args)
    await update.message.reply_text("✅ Текст обновлён!")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет прав на рассылку.")
        return
    sent = 0
    for user_id in SUBSCRIBERS:
        try:
            await context.bot.send_message(chat_id=user_id, text=user_text)
            sent += 1
        except:
            continue
    await update.message.reply_text(f"📤 Рассылка завершена. Отправлено: {sent} сообщений.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("settext", settext))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(handle_buttons, pattern="register"))
app.add_handler(CallbackQueryHandler(handle_payment, pattern="pay_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
