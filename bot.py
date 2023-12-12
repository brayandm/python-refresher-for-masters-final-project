import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import pickle
import pandas as pd
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

with open('xgboost.pkl', 'rb') as file:
    xgboost = pickle.load(file)

longitude = -122.23
latitude = 37.88
housing_median_age = 41.0
total_rooms = 880.0
total_bedrooms = 129.0
population = 322.0
households = 126.0
median_income = 8.3252
ocean_proximity_1H_OCEAN = 1
ocean_proximity_INLAND = 0
ocean_proximity_ISLAND = 0
ocean_proximity_NEAR_BAY = 0
ocean_proximity_NEAR_OCEAN = 0

data = pd.DataFrame({
    'longitude': [longitude],
    'latitude': [latitude],
    'housing_median_age': [housing_median_age],
    'total_rooms': [total_rooms],
    'total_bedrooms': [total_bedrooms],
    'population': [population],
    'households': [households],
    'median_income': [median_income],
    'ocean_proximity_<1H OCEAN': [ocean_proximity_1H_OCEAN],
    'ocean_proximity_INLAND': [ocean_proximity_INLAND],
    'ocean_proximity_ISLAND': [ocean_proximity_ISLAND],
    'ocean_proximity_NEAR BAY': [ocean_proximity_NEAR_BAY],
    'ocean_proximity_NEAR OCEAN': [ocean_proximity_NEAR_OCEAN]
})

print(xgboost.predict(data))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()
