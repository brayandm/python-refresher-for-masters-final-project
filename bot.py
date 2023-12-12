
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    return california_cities_df[california_cities_df['Name'].apply(lambda x: x.lower().replace(' ', '')) == name].head(1)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

step_per_chat = {}

data_per_chat = {}

menu = ReplyKeyboardMarkup([["📈 Predict"]])

remove_keyboard = ReplyKeyboardRemove()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot that predict prices of houses in California", reply_markup=menu)
    
    step_per_chat[update.effective_chat.id] = 0
    data_per_chat[update.effective_chat.id] = {}

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat.get(update.effective_chat.id) == None:
        step_per_chat[update.effective_chat.id] = 0
        data_per_chat[update.effective_chat.id] = {}

    if step_per_chat[update.effective_chat.id] != 0:
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Write the name of the city", reply_markup=remove_keyboard)

    step_per_chat[update.effective_chat.id] = 1

house_age_ranges = ["1-13", "14-26", "27-39", "40-52"]
house_age_ranges_markup = ReplyKeyboardMarkup([house_age_ranges])

async def get_city_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 1:
        return

    city_name = update.message.text

    city = find_city_by_name(city_name)

    if city.empty:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="City not found, try again", reply_markup=remove_keyboard)
    else:
        step_per_chat[update.effective_chat.id] = 2
        data_per_chat[update.effective_chat.id]['latitude'] = city['Latitude'].values[0]
        data_per_chat[update.effective_chat.id]['longitude'] = city['Longitude'].values[0]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Select the house age range in years", reply_markup=house_age_ranges_markup)

median_income_range = ["0.5-3.4", "3.4-6.3", "6.3-9.2", "9.2-12.1", "12.1-15.0"]
neighborhood_quality_range = ["Low", "Medium", "High", "Very High", "Ultra High"]
neighborhood_quality_range_markup = ReplyKeyboardMarkup([neighborhood_quality_range])

async def get_house_age(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 2:
        return

    house_age = update.message.text

    if house_age not in house_age_ranges:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid house age range, try again", reply_markup=house_age_ranges_markup)
        return

    data_per_chat[update.effective_chat.id]['housing_median_age'] = float((int(house_age.split('-')[0]) + int(house_age.split('-')[1])) / 2)    

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select the neighborhood quality", reply_markup=neighborhood_quality_range_markup)

    step_per_chat[update.effective_chat.id] = 3

ocean_proximity_values = ["<1H OCEAN", "INLAND", "ISLAND", "NEAR BAY", "NEAR OCEAN"]
ocean_proximity_values_display = ["<1h from Ocean", "Inland", "Island", "Near Bay", "Near Ocean"]
ocean_proximity_values_markup = ReplyKeyboardMarkup([ocean_proximity_values_display])

async def get_median_income(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 3:
        return

    neighborhood_quality = update.message.text

    if neighborhood_quality not in neighborhood_quality_range:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid neighborhood quality, try again", reply_markup=neighborhood_quality_range_markup)
        return
    
    median_income = median_income_range[neighborhood_quality_range.index(neighborhood_quality)]

    data_per_chat[update.effective_chat.id]['median_income'] = float((float(median_income.split('-')[0]) + float(median_income.split('-')[1])) / 2)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select the ocean proximity", reply_markup=ocean_proximity_values_markup)

    step_per_chat[update.effective_chat.id] = 4

async def get_ocean_proximity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat[update.effective_chat.id] != 4:
        return

    ocean_proximity = update.message.text

    if ocean_proximity not in ocean_proximity_values_display:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid ocean proximity, try again", reply_markup=ocean_proximity_values_markup)
        return
    
    ocean_proximity = ocean_proximity_values[ocean_proximity_values_display.index(ocean_proximity)]

    data_per_chat[update.effective_chat.id]['ocean_proximity_<1H OCEAN'] = 0
    data_per_chat[update.effective_chat.id]['ocean_proximity_INLAND'] = 0
    data_per_chat[update.effective_chat.id]['ocean_proximity_ISLAND'] = 0
    data_per_chat[update.effective_chat.id]['ocean_proximity_NEAR BAY'] = 0
    data_per_chat[update.effective_chat.id]['ocean_proximity_NEAR OCEAN'] = 0

    data_per_chat[update.effective_chat.id]['ocean_proximity_' + ocean_proximity] = 1

    predicting_message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Predicting...")
    predicting_message_id = predicting_message.message_id

    data_per_chat[update.effective_chat.id]['total_rooms'] = float(MEDIAN_TOTAL_ROOMS)
    data_per_chat[update.effective_chat.id]['total_bedrooms'] = float(MEDIAN_TOTAL_BEDROOMS)
    data_per_chat[update.effective_chat.id]['population'] = float(MEDIAN_POPULATION)
    data_per_chat[update.effective_chat.id]['households'] = float(MEDIAN_HOUSEHOLDS)

    data = pd.DataFrame({
    'longitude': data_per_chat[update.effective_chat.id]['longitude'],
    'latitude': data_per_chat[update.effective_chat.id]['latitude'],
    'housing_median_age': data_per_chat[update.effective_chat.id]['housing_median_age'],
    'total_rooms': data_per_chat[update.effective_chat.id]['total_rooms'],
    'total_bedrooms': data_per_chat[update.effective_chat.id]['total_bedrooms'],
    'population': data_per_chat[update.effective_chat.id]['population'],
    'households': data_per_chat[update.effective_chat.id]['households'],
    'median_income': data_per_chat[update.effective_chat.id]['median_income'],
    'ocean_proximity_<1H OCEAN': data_per_chat[update.effective_chat.id]['ocean_proximity_<1H OCEAN'],
    'ocean_proximity_INLAND': data_per_chat[update.effective_chat.id]['ocean_proximity_INLAND'],
    'ocean_proximity_ISLAND': data_per_chat[update.effective_chat.id]['ocean_proximity_ISLAND'],
    'ocean_proximity_NEAR BAY': data_per_chat[update.effective_chat.id]['ocean_proximity_NEAR BAY'],
    'ocean_proximity_NEAR OCEAN': data_per_chat[update.effective_chat.id]['ocean_proximity_NEAR OCEAN']
    }, index=[0])

    predicted_price = str(int(xgboost.predict(data)[0]))
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, 
                                    message_id=predicting_message_id, 
                                    text="The approximate price of the house is: $" + predicted_price)
                                   

    step_per_chat[update.effective_chat.id] = 0
    data_per_chat[update.effective_chat.id] = {}


async def step_analizer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if step_per_chat.get(update.effective_chat.id) == None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Press the predict button to start predicting", reply_markup=menu)
        return

    if(step_per_chat[update.effective_chat.id] == 1):
        await get_city_name(update, context)
    elif(step_per_chat[update.effective_chat.id] == 2):
        await get_house_age(update, context)
    elif(step_per_chat[update.effective_chat.id] == 3):
        await get_median_income(update, context)
    elif(step_per_chat[update.effective_chat.id] == 4):
        await get_ocean_proximity(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Press the predict button to start predicting", reply_markup=menu)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.Regex('📈 Predict'), predict))
    application.add_handler(MessageHandler(filters.Regex('(.*)'), step_analizer))
    
    application.run_polling()
