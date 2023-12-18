
import os
import telebot

from bot.config import *
from model.model import *
from telebot import types
from datetime import datetime


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, START_MESSAGE)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, HELP_MESSAGE)


@bot.message_handler(commands=['send'])
def send_photo_request(message):

    markup = types.InlineKeyboardMarkup(row_width=2)

    intervals = ["1960-1970", "1970-1980", "1980-1990", "1990-2000", "2000-2010", "2010-2020"]
    buttons = [types.InlineKeyboardButton(interval, callback_data=f"interval_{interval}") for interval in intervals]

    markup.add(*buttons)

    bot.send_message(message.chat.id, CHOOSE_TIME, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('interval_'))
def process_interval_callback(call):
    chat_id = call.message.chat.id
    chosen_interval = call.data.replace('interval_', '')
    bot.send_message(chat_id, f"{INTERVAL_CHOOSEN}: {chosen_interval}")
    bot.send_message(chat_id, PHOTO_REQUEST)
    bot.register_next_step_handler(call.message, lambda message: process_photo_step(message, chosen_interval))


@bot.message_handler(commands=['feedback'])
def get_feedback(message):
    bot.send_message(message.chat.id, FEEDBACK_REQUEST)
    bot.register_next_step_handler(message, process_feedback_step)


def process_feedback_step(message):
    try:
        chat_id = message.chat.id
        user_feedback = message.text
        save_feedback(chat_id, user_feedback)
        bot.send_message(chat_id, FEEDBACK_THANKS)
    except Exception as e:
        bot.send_message(chat_id, f"{FAILURE}: {str(e)}")


def save_feedback(chat_id, feedback_text):
    os.makedirs(FEEDBACK_DIRECTORY, exist_ok=True)

    feedback_file_path = os.path.join(FEEDBACK_DIRECTORY, f"{chat_id}_feedback.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_entry = f"{timestamp}\n{feedback_text}\n\n"

    with open(feedback_file_path, "a", encoding="utf-8") as feedback_file:
        feedback_file.write(feedback_entry)


def process_photo_step(message, interval):
    try:
        chat_id = message.chat.id
        if message.photo:
            photo_id = message.photo[-1].file_id
            file_info = bot.get_file(photo_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = os.path.join(IMAGE_DIRETORY, f"{chat_id}_photo.jpg")
            with open(file_path, "wb") as new_file:
                new_file.write(downloaded_file)

            bot.send_message(chat_id, IMAGE_SUCCESS)

            mood = predict_mood(file_path)
            print(mood)
            playlist_message = format_playlist(get_playlist(mood, interval), mood)
            bot.send_message(chat_id, playlist_message)
        else:
            bot.send_message(chat_id, IMAGE_MISTAKE)
    except Exception as e:
        bot.send_message(chat_id, f"{FAILURE}: {str(e)}")


def format_playlist(playlist, mood):
    playlist_message = MOOD_MESSAGE_TEMPLATE.format(mood=mood)
    for idx, song in enumerate(playlist, start=1):
        playlist_message += f"{idx}. {song['name']} by {song['artist']} - {song['id']}\n"
    return playlist_message
