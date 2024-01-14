from environs import Env
import logging

import redis
from telegram import Update, Bot, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from functools import partial

from telegram_log import TelegramLogsHandler
from utils import new_question, reply_markup


CHOOSING, ANSWERING = range(2)

logger = logging.getLogger('Logger')


def start(update, _):

    update.message.reply_text('Здравствуйте! Я бот для викторин!')
    user = update.effective_user

    update.message.reply_text(
        f'{user.name}\nДавай поиграем!\nДля вопроса нажми «Новый вопрос»',
        reply_markup=reply_markup,
     )
    return CHOOSING


def cancel(update, _):
    update.message.reply_text('Досвидания!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def handle_new_question_request(update, context):

    question, answer = new_question()

    context.user_data['answer'] = answer
    update.message.reply_text(question)
    update.message.reply_text(answer)

    return ANSWERING


def handle_solution_attempt(update, context):

    correct_answer = context.user_data['answer']
    user_answer = update.message.text

    if user_answer.lower() == correct_answer.lower():
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        update.message.reply_text(text, reply_markup=reply_markup)
        return ANSWERING
    else:
        text = 'Неправильно… Попробуешь ещё раз?'
        update.message.reply_text(text, reply_markup=reply_markup)


def handle_score_request(update, context):

    print('Счет')


def handle_show_answer(update, context):

    print('Сдаться')


def main():
    env = Env()
    env.read_env()

    logger_bot = Bot(token=env.str('TELEGRAM_LOG_TOKEN'))
    chat_id = env.str('TELEGRAM_CHAT_ID')

    updater = Updater(env.str('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logger_bot, 'ТГ Викторины', chat_id))

    logger.info('Бот запущен')

    redis_db = redis.Redis(host='localhost', port=6379, protocol=3, db=0)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^(Новый вопрос)$'), handle_new_question_request),
                MessageHandler(Filters.regex('^(Мой счет)$'), handle_score_request)],
            ANSWERING: [
                MessageHandler(Filters.regex('^(Новый вопрос)$'), handle_new_question_request),
                MessageHandler(Filters.regex('^(Сдаться)$'), handle_show_answer),
                MessageHandler(Filters.regex('^(Мой счет)$'), handle_score_request),
                MessageHandler(Filters.text, handle_solution_attempt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
