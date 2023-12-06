from environs import Env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здравствуйте!')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main():
    env = Env()
    env.read_env()

    updater = Updater(env.str('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
