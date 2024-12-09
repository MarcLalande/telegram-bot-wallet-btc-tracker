from typing import Final
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue, Updater
import time
import requests
import datetime
import requests
import pytz

#logging.basicConfig(level=logging.DEBUG)
TOKEN = '7346472629:AAHKAXoGGf69sRh-ldY1ikna09lmiyjB93E'
BOT_USERNAME: Final = '@mr_100_tracker_bot'
my_id : Final = '1494792751'
WALLET_ADDRESS_MR_100 = '1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP'
API_ROUTE = 'https://blockchain.info/rawaddr/1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP'
API_ROUTE2= 'https://mempool.space/api/address/1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP'
count = 0


local_timezone = pytz.timezone('Europe/Amsterdam')
negative_transactions = []
positive_transactions = []
time_daily = datetime.time(hour=00, minute=00,
                           second=00).replace(tzinfo=local_timezone)



def InitialWalletData():
    global count
    response = requests.get(API_ROUTE2)
    if response.status_code == 200:
        data = response.json()

        income= data['chain_stats']['funded_txo_sum']
        outcome =data['chain_stats']['spent_txo_sum']

        previous_balance = (income-outcome)/1e8
        return previous_balance
    else:
        print('failed to get balance, will try again in 3 min.')
        time.sleep(60 * 3)
        count += 1
        if count == 2:
            previous_balance = 0
            return previous_balance
        else:
            InitialWalletData()


previous_balance = InitialWalletData()


async def fetchDataDiff(context: ContextTypes.DEFAULT_TYPE) -> None:

    global previous_balance
    global negative_transactions
    global positive_transactions

    response = requests.get(API_ROUTE2)
    if response.status_code == 200:
        data = response.json()

        income= data['chain_stats']['funded_txo_sum']
        outcome =data['chain_stats']['spent_txo_sum']

        new_balance = (income-outcome)/1e8
        if previous_balance >= new_balance:
            operation = abs(previous_balance - new_balance)
            if operation > 10:
                positive_transactions.append(operation)
                await bot.send_message(
                    chat_id='@mr100News',
                    text=
                    f'Mr 100 has Sold : {abs(previous_balance - new_balance)} BTC'
                )

            elif operation < -10:
                negative_transactions.append(operation)
                await bot.send_message(
                    chat_id='@mr100News',
                    text=
                    f' Mr 100 has sold : {abs(previous_balance - new_balance)} BTC'
                )

            previous_balance = new_balance
        if previous_balance < new_balance:
            operation = abs(previous_balance - new_balance)
            if operation > 10:
                positive_transactions.append(operation)
                await bot.send_message(
                    chat_id='@mr100News',
                    text=
                    f'Mr 100 has bought : {abs(previous_balance - new_balance)} BTC'
                )

            elif operation < -10:
                negative_transactions.append(operation)
                await bot.send_message(
                    chat_id='@mr100News',
                    text=
                    f' Mr 100 has sold : {abs(previous_balance - new_balance)} BTC'
                )

            previous_balance = new_balance
        else:
            await bot.send_message(
                chat_id=my_id,
                text=
                f' Mr 100 has Nothing but requests works'
            )
            print('No changes in the wallet for now')

    else:
        print('Failed to fetch data from the API.')



async def daily_count(context: ContextTypes.DEFAULT_TYPE) -> None:

    print('is triggered')
    global negative_transactions
    global positive_transactions
    await bot.send_message(
        chat_id='@mr100News',
        text=
        f' Mr 100 has bought : {sum(positive_transactions)} and sold : {sum(negative_transactions)} BTC .  the result is {sum(positive_transactions)-sum(negative_transactions)}'
    )
    await bot.send_message(
        chat_id=my_id,
        text=
        f' daily count has happened. See news'
    )
    negative_transactions = []
    positive_transactions = []


# Usage

message = "Bot is alive"
#url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={my_id}&text={message}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Bot has started...')
    message_type: str = update.message.chat.type
async def informAdmin(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    await bot.send_message(
        chat_id=my_id,
        text=
        f'Bot is working. Current time is: {now.time()}'
    )




if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    bot = telegram.Bot(TOKEN)

    j = app.job_queue




    j.run_repeating(fetchDataDiff, interval=30 * 60, first=0)#every 10 min print if changes have been made 
    j.run_repeating(informAdmin, interval=10 * 60, first=0) # send data to specify user about bot working
    j.run_daily(daily_count, time_daily, days=tuple(range(7))) #every day print changes from yesterday



    print('Polling....')

    app.run_polling(poll_interval=3)
