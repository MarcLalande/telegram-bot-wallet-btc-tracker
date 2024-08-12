from typing import Final
import telegram
from background import keep_alive  #импорт функции для поддержки работоспособности
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue, Updater
import threading
import time
import requests
import datetime
from flask import Flask
import os

keep_alive()
TOKEN = #########################YOUR TOKEN
BOT_USERNAME: Final =  #########################Your bot name
WALLET_ADDRESS_MR_100 = '1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP'
API_ROUTE = 'https://blockchain.info/rawaddr/1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP'
count = 0
import pytz

local_timezone = pytz.timezone('Europe/Amsterdam')
negative_transactions = []
positive_transactions = []
time_daily = datetime.time(hour=00, minute=00,
                           second=00).replace(tzinfo=local_timezone)
import asyncio


def initial_req_wallet():
    global count
    response = requests.get(API_ROUTE)
    if response.status_code == 200:
        data = response.json()
        previous_balance = data['final_balance'] / 1e8
        return previous_balance
    else:
        print('failed to get balance, will try again in 3 min.')
        time.sleep(60 * 30)
        count += 1
        if count == 2:
            previous_balance = 0
            return previous_balance
        else:
            initial_req_wallet()


previous_balance = initial_req_wallet()


async def fetch_data_balance(context: ContextTypes.DEFAULT_TYPE) -> None:

    global previous_balance
    global negative_transactions
    global positive_transactions
    print('got here')
    print(positive_transactions, 'positives', 'n', negative_transactions)

    response = requests.get(API_ROUTE)
    if response.status_code == 200:
        data = response.json()
        new_balance = data[
            'final_balance'] / 1e8  # Convert balance from satoshis to BTC

        if previous_balance != new_balance:
            operation = abs(previous_balance - new_balance)
            if operation > 10:
                positive_transactions.append(operation)
                await bot.send_message(
                    chat_id=-1002249261036,
                    text=
                    f'Mr 100 has bought : {abs(previous_balance - new_balance)} BTC'
                )

            elif operation < -10:
                negative_transactions.append(operation)
                await bot.send_message(
                    chat_id=-1002249261036,
                    text=
                    f' Mr 100 has sold : {abs(previous_balance - new_balance)} BTC'
                )

            previous_balance = new_balance

        else:

            print('nothing happening')

    else:
        print('Failed to fetch data from the API.')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('started function')

    await update.message.reply_text('Getting')


async def monitor_mr_100_command(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('monitor mr100')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Need help!')


async def daily_count(context: ContextTypes.DEFAULT_TYPE) -> None:

    print('is triggered')
    global negative_transactions
    global positive_transactions
    await bot.send_message(
        chat_id=-1002249261036,
        text=
        f' Mr 100 has bought : {sum(positive_transactions)} and sold : {sum(negative_transactions)} BTC .  the result is {sum(positive_transactions)-sum(negative_transactions)}'
    )
    negative_transactions = []
    positive_transactions = []


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('bot is starting')
    message_type: str = update.message.chat.type


async def bot_is_working(context: ContextTypes.DEFAULT_TYPE) -> None:
    print('Bot is working')
    await asyncio.sleep(0)  # You can change the sleep duration as needed


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    bot = telegram.Bot(TOKEN)

    j = app.job_queue

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('about', monitor_mr_100_command))
    j.run_repeating(bot_is_working, interval=3600 * 6, first=0)
    j.run_repeating(fetch_data_balance, interval=30 * 60, first=0)
    j.run_daily(daily_count, time_daily, days=tuple(range(7)))

    print('Polling....')

    app.run_polling(poll_interval=3)
