from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Eu sou o NanoFin, seu assistente financeiro pessoal. Vamos manter suas finanças no controle! 💰"
    )


def main():
    app = ApplicationBuilder().token("7340435006:AAGKp0pSuk6LwxVdypu2fDJa4tR2jmY_bUY").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
