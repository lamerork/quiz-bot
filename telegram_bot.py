from environs import Env
import logging

import redis
from telegram import Bot, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from telegram_log import TelegramLogsHandler
from quiz_question import question_new


CHOOSING, ANSWERING = range(2)

logger = logging.getLogger('Logger')

keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def start(update, context):

    update.message.reply_text('Здравствуйте! Я бот для викторин!')
    user = update.effective_user

    update.message.reply_text(
        f'{user.name}\nДля вопроса нажми «Новый вопрос»',
        reply_markup=reply_markup,
     )

    r = redis.Redis(host='localhost', port=6379, protocol=3, db=0, decode_responses=True)

    context.user_data['redis'] = r

    context.user_data['score'] = 0
    return CHOOSING


def cancel(update, _):
    update.message.reply_text('Досвидания!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def handle_new_question_request(update, context):

    question, answer = question_new()

    update.message.reply_text(question)

    context.user_data['redis'].hset(update.message.chat.id, mapping={
        'answer': answer,
        'question': question
    })

    return ANSWERING


def handle_solution_attempt(update, context):

    correct_answer = context.user_data['redis'].hgetall(update.message.chat.id)['answer']
    user_answer = update.message.text

    if user_answer.lower() == correct_answer.lower():
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data['score'] += 1
        return CHOOSING
    else:
        text = 'Неправильно… Попробуешь ещё раз?'
        update.message.reply_text(text, reply_markup=reply_markup)


def handle_score_request(update, context):

    score = context.user_data['score']
    text = f'Ваш счет: {score}'
    update.message.reply_text(text, reply_markup=reply_markup)


def handle_show_answer(update, context):

    answer = context.user_data['redis'].hgetall(update.message.chat.id)['answer']
    text = f'Правильны ответ:\n{answer}\n\nДля следующего вопроса нажми «Новый вопрос»'
    update.message.reply_text(text, reply_markup=reply_markup)

    return CHOOSING


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
