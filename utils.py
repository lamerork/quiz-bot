from os import listdir
from os.path import join
from random import choice
import re

from telegram import ReplyKeyboardMarkup

keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def new_question():
    path = 'quiz-questions'

    filename = choice(listdir(path))

    with open(join(path, filename), 'r', encoding='KOI8-R') as f:
        text = f.read()

    questions = re.findall(r'Вопрос \d+:\s(.*?)\sОтвет', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.*?)\.\s\s', text)

    question, answer = choice(list(zip(questions, answers)))

    answer = re.sub(r'\([^()]*\)|\[[^()]*\]', '', answer)
    answer = re.sub(r'[$|&|!|,|.|\"]', '', answer)
    answer = re.sub(r'[\d\.]', '', answer)
    answer = re.sub(r'^\s+|\s+$', '', answer)

    return question, answer


def check_answer(corre):
    pass
