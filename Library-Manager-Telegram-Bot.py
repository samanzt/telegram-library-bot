# ============================================ imports ==============================================
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (CommandHandler, MessageHandler, ConversationHandler, filters, Application, ContextTypes,
                          CallbackQueryHandler)
import database

# ============================================ setting =============================================
TOKEN = 'TOKEN'

BOOK_NAME = 0
AUTHOR_NAME = 1
BOOK_YEAR = 2
BOOK_CATEGORY = 3
EDIT_BOOK_SELECT=4
EDIT_CHOICE = 5
EDIT_BOOK_NAME = 6
EDIT_AUTHOR_NAME = 7
EDIT_BOOK_YEAR = 8
EDIT_BOOK_CATEGORY = 9
SEARCH_BOOK = 10
DELETE_BOOK = 11

keyboard = [[InlineKeyboardButton("افزودن", callback_data="add"),
             InlineKeyboardButton("لیست", callback_data="list")],
            [InlineKeyboardButton("جستجو", callback_data="search"), ]]
cancel_button = [[InlineKeyboardButton("لغو", callback_data="cancel"), ]]
back_button = [[InlineKeyboardButton("بازگشت", callback_data="back")]]
reply_markup = InlineKeyboardMarkup(keyboard)
cancel_markup = InlineKeyboardMarkup(cancel_button)
back_markup = InlineKeyboardMarkup(back_button)


# ==================================================== start ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    get_books(context)
    await update.message.reply_text("به بات مدیریت کتابخانه خوش آمدید\n"
                                    "عملیات مور نظر خود را انتخاب کنید", reply_markup=reply_markup)
    return ConversationHandler.END

async def show_page(update, text, markup=None):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=markup)
    else:
        await update.message.reply_text(text, reply_markup=markup)


def get_books(context: ContextTypes.DEFAULT_TYPE):
    context.user_data["books"] = []
    for book in database.view_all():
        context.user_data["books"].append({"id": book[0],
                                           "title": book[1],
                                           "author": book[2],
                                           "year": book[3],
                                           "category": book[4]})


# ==================================================== add ==========================================
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "books" not in context.user_data:
        context.user_data["books"] = []

    if update.message:
        await update.message.reply_text(
            "نام کتاب را وارد کنید\n"
            "برای توقف عملیات /cancel را وارد کنید"
        )
    else:
        await show_page(update, "نام کتاب را وارد کنید\n"
                                "برای توقف عملیات /cancel را وارد یا دکمه زیر را فشار دهید", cancel_markup)
    return BOOK_NAME


async def get_book_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["book_name"] = update.message.text
    for book in context.user_data["books"]:
        if book["title"].strip().lower() == update.message.text.strip().lower():
            await show_page(update, "کتاب مورد نظر در کتابخانه موجود است\nلطفا نام کتاب دیگری را وارد کنید")
            return BOOK_NAME
    await show_page(update, "نام نویسنده را وارد کنید", cancel_markup)
    return AUTHOR_NAME


async def get_author_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["author_name"] = update.message.text
    await show_page(update, "سال انتشار کتاب را وارد کنید", cancel_markup)
    return BOOK_YEAR


async def get_book_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        int(update.message.text)
    except ValueError:
        await update.message.reply_text("فقط عدد وارد کنید",reply_markup=cancel_markup)
    context.user_data["books_year"] = update.message.text
    await show_page(update, "ژانر کتاب را وارد کنید", cancel_markup)
    return BOOK_CATEGORY


async def get_book_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["book_category"] = update.message.text
    context.user_data["books"].append({
        "title": context.user_data["book_name"],
        "author": context.user_data["author_name"],
        "year": context.user_data["books_year"],
        "category": context.user_data["book_category"]})
    database.insert(context.user_data["book_name"], context.user_data["author_name"], context.user_data["books_year"],
                    context.user_data["book_category"])
    await show_page(update, "عملیات با موفقیت انجام شد", back_markup)
    return ConversationHandler.END


# ==================================================== list ==========================================
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_books(context)
    books = context.user_data.get("books", [])
    if not books:
        await show_page(update, "هیچ کتابی وارد کتابخانه نشده است", back_markup)
        return
    text = ""
    for index, book in enumerate(books, start=1):
        text += (f"📚{index}.\n"
                f" 📖نام کتاب: {book['title']}\n"
                 f" ✍️نام نویسنده: {book['author']}\n"
                 f" 🗓️سال انتشار:️ {book['year']}\n"
                 f" 🎭ژانر: {book['category']}\n\n")
    edit_and_delete_keyboard = [[InlineKeyboardButton("ویرایش کتاب", callback_data="edit_book"),
                                 InlineKeyboardButton("حذف کتاب", callback_data="delete_book")],
                                [InlineKeyboardButton("بازگشت", callback_data="back")]]
    edit_and_delete_markup = InlineKeyboardMarkup(edit_and_delete_keyboard)
    await show_page(update, text, markup=edit_and_delete_markup)


# ==================================================== cancel and back ==========================================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("عملیات متوقف شد ")
        return ConversationHandler.END
    else:
        await show_page(update, "عملیات متوقف شد ", back_markup)
        return ConversationHandler.END


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page(update, "عملیات خود را انتخاب کنید", reply_markup)


# ==================================================== delete ==========================================
async def delete_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get("books")
    text = ""
    for index, book in enumerate(books, start=1):
        text += (f"📚{index}.\n"
                 f" 📖نام کتاب: {book['title']}\n"
                 f" ✍️نام نویسنده: {book['author']}\n"
                 f" 🗓️سال انتشار:️ {book['year']}\n"
                 f" 🎭ژانر: {book['category']}\n\n")
    text += "شماره کتاب مورد نظر را وارد کنید"
    await show_page(update, text, cancel_markup)
    return DELETE_BOOK


async def delete_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get("books")
    try:
        number = int(update.message.text)
    except ValueError:
        await update.message.reply_text("فقط شماره وارد کنید", reply_markup=cancel_markup)
        return DELETE_BOOK
    if number < 1 or number > len(books):
        await update.message.reply_text("شماره معتبر نیست.",reply_markup=back_markup)
        return ConversationHandler.END
    number = number - 1
    index=books[number]
    print(index["id"])
    database.delete(index["id"])
    await show_page(update,"عملیات با موفقیت انجام شد",back_markup)
    return ConversationHandler.END

# ==================================================== edit ==========================================
async def edit_book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get("books")
    text = ""
    for index, book in enumerate(books, start=1):
        text += (f"📚{index}.\n"
                f" 📖نام کتاب: {book['title']}\n"
                 f" ✍️نام نویسنده: {book['author']}\n"
                 f" 🗓️سال انتشار:️ {book['year']}\n"
                 f" 🎭ژانر: {book['category']}\n\n")
    text+= "شماره کتاب مورد نظر را وارد کنید"
    await show_page(update, text, cancel_markup)
    return EDIT_BOOK_SELECT

async def get_edit_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get("books")
    try:
        number = int(update.message.text)
    except ValueError:
        await update.message.reply_text("فقط شماره وارد کنید",reply_markup=cancel_markup)
        return EDIT_BOOK_SELECT
    if number < 1 or number > len(books):
        await update.message.reply_text("شماره معتبر نیست.",reply_markup=back_markup)
        return EDIT_BOOK_SELECT
    context.user_data["edit_index"] = number - 1

    edit_keyboard = [
        [
            InlineKeyboardButton("نام کتاب", callback_data="edit_name"),
            InlineKeyboardButton("نویسنده", callback_data="edit_author")
        ],
        [
            InlineKeyboardButton("سال انتشار", callback_data="edit_year"),
            InlineKeyboardButton("ژانر", callback_data="edit_category")
        ],
        [
            InlineKeyboardButton("لغو", callback_data="cancel")
        ]
    ]

    await show_page(update,"چه بخشی را می‌خواهید ویرایش کنید؟",InlineKeyboardMarkup(edit_keyboard))
    return EDIT_CHOICE
async def edit_choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "edit_name":
        await show_page(update, "نام جدید کتاب را وارد کنید", cancel_markup)
        return EDIT_BOOK_NAME
    if query.data == "edit_author":
        await show_page(update, "نام جدید نویسنده را وارد کنید", cancel_markup)
        return EDIT_AUTHOR_NAME
    if query.data == "edit_year":
        await show_page(update, "سال جدید را وارد کنید", cancel_markup)
        return EDIT_BOOK_YEAR
    if query.data == "edit_category":
        await show_page(update, "ژانر جدید را وارد کنید", cancel_markup)
        return EDIT_BOOK_CATEGORY


async def get_edited_book_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["edit_index"]
    books = context.user_data.get("books")
    database.update(id=books[index]['id'],title=update.message.text,author=books[index]["author"],year=books[index]["year"],category=books[index]["category"])
    await update.message.reply_text("نام کتاب ویرایش شد", reply_markup=back_markup)
    get_books(context)
    return ConversationHandler.END


async def get_edited_author_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["edit_index"]
    books = context.user_data.get("books")
    books[index]["author"] = update.message.text
    database.update(id=books[index]['id'],title=books[index]["title"],author=update.message.text,year=books[index]["year"],category=books[index]["category"])
    await update.message.reply_text("نام نویسنده کتاب ویرایش شد", reply_markup=back_markup)
    return ConversationHandler.END


async def get_edited_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["edit_index"]
    books = context.user_data.get("books")
    try:
        int(update.message.text)
    except ValueError:
        await update.message.reply_text("فقط عدد وارد کنید",reply_markup=cancel_markup)
    database.update(id=books[index]['id'], title=books[index]["title"], author=books[index]["author"],year=update.message.text, category=books[index]["category"])
    await update.message.reply_text( "سال انتشار کتاب ویرایش شد", reply_markup=back_markup)
    get_books(context)
    return ConversationHandler.END


async def get_edited_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["edit_index"]
    books = context.user_data.get("books")
    database.update(id=books[index]['id'], title=books[index]["title"], author=books[index]["author"],year=books[index]["year"], category=update.message.text)
    await show_page(update, "ژانر کتاب ویرایش شد", back_markup)
    get_books(context)
    return ConversationHandler.END


# ==================================================== search ==========================================
async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_books(context)
    await show_page(update, "نام کتاب مورد نظر را وارد کنید")
    return SEARCH_BOOK


async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get("books", [])
    for book in books:
        if book["title"].strip().lower() == update.message.text.strip().lower():
            await show_page(update,
                            f"📖{book['title']}\n"
                            f"✍️{book['author']}\n"
                            f"سال انتشار: 🗓️{book['year']}\n"
                            f"🎭{book['category']}\n\n", back_markup)
            return ConversationHandler.END
    await show_page(update, "کتاب مورد نظر پیدا نشد", back_markup)
    return ConversationHandler.END


# ==================================================== setting ==========================================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_start),
                  CallbackQueryHandler(add_start, pattern="add"),
                  CallbackQueryHandler(edit_book_start, pattern="^edit_"),
                  CallbackQueryHandler(search_start, pattern="search"),
                  CallbackQueryHandler(delete_book_start, pattern="delete_book"), ],
    states={BOOK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_name)],
            AUTHOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_author_name)],
            BOOK_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_year)],
            BOOK_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_book_category)],
            DELETE_BOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_book)],
            EDIT_BOOK_SELECT:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_edit_number)],
            EDIT_CHOICE: [CallbackQueryHandler(edit_choice_handler, pattern="^edit_")],
            EDIT_BOOK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edited_book_name)],
            EDIT_AUTHOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edited_author_name)],
            EDIT_BOOK_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edited_year)],
            EDIT_BOOK_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_edited_category)],
            SEARCH_BOOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_book)]},
    fallbacks=[CommandHandler("cancel", cancel), (CallbackQueryHandler(cancel, pattern="cancel"))]
)
app.add_handler(conversation_handler)
app.add_handler(CommandHandler("list", show_list))
app.add_handler(CallbackQueryHandler(show_list, pattern="list"))
app.add_handler(CallbackQueryHandler(back, pattern="back"))

app.run_polling()
