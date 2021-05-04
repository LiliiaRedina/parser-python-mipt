from telegram.ext import CommandHandler
from telegram.ext import Updater
import bot

bot = bot.Bot()

updater = Updater(bot.BOT_TOKEN)

dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", bot.start))
dispatcher.add_handler(CommandHandler("help", bot.help_command))
dispatcher.add_handler(CommandHandler('new_docs', bot.new_docs))
dispatcher.add_handler(CommandHandler('new_topics', bot.new_topics))
dispatcher.add_handler(CommandHandler('topic', bot.topic))
dispatcher.add_handler(CommandHandler('doc', bot.doc))
dispatcher.add_handler(CommandHandler('describe_doc', bot.describe_doc))
dispatcher.add_handler(CommandHandler('describe_topic', bot.describe_topic))
dispatcher.add_handler(CommandHandler('words', bot.words))
dispatcher.add_handler(CommandHandler('drop_parser', bot.drop_parser))

updater.start_polling()

updater.idle()
