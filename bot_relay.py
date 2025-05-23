import os, json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN      = os.getenv("TOKEN")
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        return json.load(open(USERS_FILE))
    return []

def save_users(u):
    json.dump(u, open(USERS_FILE, "w"))

def start_cmd(update: Update, ctx: CallbackContext):
    update.message.reply_text(
        "👋 Salut ! Tape /register pour recevoir les logs, ou /unregister pour arrêter."
    )

def register_cmd(update: Update, ctx: CallbackContext):
    users = load_users()
    cid   = update.effective_chat.id
    if cid not in users:
        users.append(cid); save_users(users)
        update.message.reply_text("✅ Inscrit : tu recevras désormais les logs.")
    else:
        update.message.reply_text("⚠️ Tu es déjà inscrit.")

def unregister_cmd(update: Update, ctx: CallbackContext):
    users = load_users()
    cid   = update.effective_chat.id
    if cid in users:
        users.remove(cid); save_users(users)
        update.message.reply_text("❌ Désinscrit : tu ne recevras plus rien.")
    else:
        update.message.reply_text("⚠️ Tu n’étais pas inscrit.")

def forward_logs(update: Update, ctx: CallbackContext):
    users = load_users()
    msg   = update.message
    for uid in users:
        try:
            if msg.text:
                ctx.bot.send_message(chat_id=uid, text=f"[LOG] {msg.text}")
            elif msg.photo:
                pid = msg.photo[-1].file_id
                ctx.bot.send_photo(chat_id=uid, photo=pid, caption="[LOG] photo")
            elif msg.document:
                did = msg.document.file_id
                ctx.bot.send_document(chat_id=uid, document=did, caption="[LOG] fichier")
        except Exception as e:
            print("Erreur →", e)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start",      start_cmd))
    dp.add_handler(CommandHandler("register",   register_cmd))
    dp.add_handler(CommandHandler("unregister", unregister_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_logs))
    dp.add_handler(MessageHandler(Filters.photo,      forward_logs))
    dp.add_handler(MessageHandler(Filters.document,   forward_logs))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
