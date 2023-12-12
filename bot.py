import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import pickle
import pandas as pd
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MEDIAN_TOTAL_ROOMS = os.getenv('MEDIAN_TOTAL_ROOMS')
MEDIAN_TOTAL_BEDROOMS = os.getenv('MEDIAN_TOTAL_BEDROOMS')
MEDIAN_POPULATION = os.getenv('MEDIAN_POPULATION')
MEDIAN_HOUSEHOLDS = os.getenv('MEDIAN_HOUSEHOLDS')

with open('xgboost.pkl', 'rb') as file:
    xgboost = pickle.load(file)

california_cities_df = pd.read_csv('data/california_cities.csv')

def find_city_by_name(name):
    name = name.lower().replace(' ', '')
    return california_cities_df[california_cities_df['Name'].str.lower().replace(' ', '') == name].head(1)

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

step_per_chat = {}

data_per_chat = {}

menu = ReplyKeyboardMarkup([["📈 Predict"]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot that predict prices of houses in California", reply_markup=menu)
    
    step_per_chat[update.effective_chat.id] = 0
    data_per_chat[update.effective_chat.id] = {}

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 0:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Write the name of the city")

    step_per_chat[update.effective_chat.id] = 1

async def get_city_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 1:
        return

    city_name = update.message.text

    city = find_city_by_name(city_name)

    if city.empty:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="City not found, try again")
    else:
        step_per_chat[update.effective_chat.id] = 2
        data_per_chat[update.effective_chat.id]['latitude'] = city['Latitude'].values[0]
        data_per_chat[update.effective_chat.id]['longitude'] = city['Longitude'].values[0]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="City found with coordinates: " + str(city['Longitude'].values[0]) + ", " + str(city['Latitude'].values[0]))


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Regex('📈 Predict'), predict))
    application.add_handler(MessageHandler(filters.Regex('(.*)'), get_city_name))
    
    application.run_polling()
