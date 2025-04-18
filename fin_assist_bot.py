import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from dotenv import load_dotenv
from datetime import datetime
import sqlite3

load_dotenv()

TOKEN = "7340435006:AAGKp0pSuk6LwxVdypu2fDJa4tR2jmY_bUY"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(f"Olá {user.first_name}! Eu sou seu assistente financeiro. Use os comandos para gerenciar suas finanças.")

async def add_expense(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    try:
        amount = float(context.args[0])
        category = context.args[1]
        description = " ".join(context.args[2:])
        
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (user_id INTEGER, amount REAL, category TEXT, description TEXT, date TEXT)''')
        
        cursor.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                       (user.id, amount, category, description, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"Despesa de R${amount} registrada na categoria {category} com a descrição: {description}.")
    
    except (IndexError, ValueError):
        await update.message.reply_text("Por favor, use o formato correto: /despesa <valor> <categoria> <descrição>")

async def generate_report(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user.id,))
        expenses = cursor.fetchall()
        
        conn.close()
        
        df = pd.DataFrame(expenses, columns=["User ID", "Amount", "Category", "Description", "Date"])
        
        report_filename = f"relatorio_{user.id}.csv"
        df.to_csv(report_filename, index=False)
        
        await update.message.reply_document(document=open(report_filename, 'rb'))
        
    except Exception as e:
        await update.message.reply_text("Ocorreu um erro ao gerar o relatório.")
        logger.error(f"Erro ao gerar relatório: {e}")

async def show_graph(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user.id,))
        categories = cursor.fetchall()
        
        conn.close()
        
        categories_df = pd.DataFrame(categories, columns=["Category", "Amount"])
        categories_df.plot(kind="bar", x="Category", y="Amount", legend=False)
        
        graph_filename = f"grafico_{user.id}.png"
        plt.savefig(graph_filename)
        
        await update.message.reply_photo(photo=open(graph_filename, 'rb'))
    
    except Exception as e:
        await update.message.reply_text("Ocorreu um erro ao gerar o gráfico.")
        logger.error(f"Erro ao gerar gráfico: {e}")

async def backup(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    try:
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user.id,))
        expenses = cursor.fetchall()
        
        conn.close()
        
        backup_filename = f"backup_{user.id}.csv"
        df = pd.DataFrame(expenses, columns=["User ID", "Amount", "Category", "Description", "Date"])
        df.to_csv(backup_filename, index=False)
        
        await update.message.reply_document(document=open(backup_filename, 'rb'))
    
    except Exception as e:
        await update.message.reply_text("Erro ao gerar o backup.")
        logger.error(f"Erro ao fazer backup: {e}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("despesa", add_expense))
    application.add_handler(CommandHandler("relatorio", generate_report))
    application.add_handler(CommandHandler("grafico", show_graph))
    application.add_handler(CommandHandler("backup", backup))

    application.run_polling()

if __name__ == "__main__":
    main()
