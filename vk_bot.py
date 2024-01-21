from environs import Env
import redis
import logging

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from telegram import Bot

from common import new_question
from telegram_log import TelegramLogsHandler


logger = logging.getLogger('Logger')


def handle_new_question_request(event, redis_db):

    question, answer = new_question()

    redis_db.hset(event.user_id, mapping={
        'answer': answer,
        'question': question
    })

    return question


def handle_solution_attempt(event, redis_db):

    correct_answer = redis_db.hgetall(event.user_id)['answer']
    user_answer = event.text

    if user_answer.lower() == correct_answer.lower():
        text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        redis_db.incr(f'{event.user_id}_score')
    else:
        text = 'Неправильно… Попробуешь ещё раз?'

    return text


def handle_score_request(event, redis_db):

    score = redis_db.get(f'{event.user_id}_score')
    return f'Ваш счет: {score}'


def handle_show_answer(event, redis_db):

    answer = redis_db.hgetall(event.user_id)['answer']
    return f'Правильны ответ:\n{answer}\n\nДля следующего вопроса нажми «Новый вопрос»'


def main():

    env = Env()
    env.read_env()

    logger_bot = Bot(token=env.str('TELEGRAM_LOG_TOKEN'))
    chat_id = env.str('TELEGRAM_CHAT_ID')

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(logger_bot, 'ВК Викторины', chat_id))

    vk_session = vk.VkApi(token=env.str('VK_TOKEN'))
    vk_api = vk_session.get_api()

    redis_db = redis.Redis(host='localhost', port=6379, protocol=3, db=0, decode_responses=True)

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет')

    logger.info('Бот запущен')

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        if event.text == 'Новый вопрос':
            text = handle_new_question_request(event, redis_db)

        elif event.text == 'Сдаться':
            text = handle_show_answer(event, redis_db)

        elif event.text == 'Мой счет':
            text = handle_score_request(event, redis_db)

        elif redis_db.exists(event.user_id):
            text = handle_solution_attempt(event, redis_db)

        else:
            text = f'Здравствуйте! Я бот для викторин!\nДля вопроса нажми «Новый вопрос»'

        vk_api.messages.send(
            user_id=event.user_id,
            message=text,
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id())


if __name__ == "__main__":
    main()
