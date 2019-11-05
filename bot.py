import os
from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from config import TG_TOKEN
from config import TG_API_URL

from dotenv import load_dotenv
load_dotenv()

path_to_fingerprint_bot = os.getenv('PATH_TO_FINGERPRINT_BOT')
recognition_file_name = os.getenv('RECOGNITION_FILE_NAME')

def do_start(update, context):
  context.bot.send_message(
  chat_id = update.message.chat_id,
    text = 'Hello! Please send me a voice message and I will try to recognize the song playing.'
  )

def do_echo(update, context):
  chat_id = update.message.chat_id
  if update.message.voice:
    context.bot.send_message(chat_id = chat_id, text = 'Thank you for you voice message! Please, wait while I am analyzing...')

    file_id = update.message.voice.file_id
    newFile = context.bot.get_file(file_id)
    file_name = f'{chat_id}{file_id}.ogg'
    newFile.download(file_name)

    cwd = os.getcwd()
    recognition_result = os.popen(f'cd {path_to_fingerprint_bot} && python ./{recognition_file_name} -f {cwd}/{file_name} && cd {cwd}').read()
    song_in_text = recognition_result.split('song: ', 1)
    if len(song_in_text) > 1:
      song = song_in_text[1].split('\n', 1)[0][:-7]
      confidence = recognition_result.split('confidence: ', 1)[1].split('\n', 1)[0][:-4]

      if int(confidence) < 35:
        context.bot.send_message(chat_id = chat_id, text = 'Sorry... I couldn\'t find anything. Please, try again.')
      else:
        answer = f'Result:\n\n{song}'
        context.bot.send_message(chat_id = chat_id, text = answer)
    else:
      no_match = 'Sorry... I couldn\'t find anything. Please, try again.'
      context.bot.send_message(chat_id = chat_id, text = no_match)

    os.system(f'rm {file_name}')
  else:
    context.bot.send_message(chat_id, 'Please, send me valid voice message. I can\'t recognize what you sent me.')


def main():
    bot = Bot(
        token = TG_TOKEN,
	base_url = TG_API_URL,
    )
    updater = Updater(TG_TOKEN, use_context=True)

    start_handler = CommandHandler('start', do_start)
    message_handler = MessageHandler(Filters.text, do_echo)
    voice_handler = MessageHandler(Filters.voice, do_echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(voice_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

