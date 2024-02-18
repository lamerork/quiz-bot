from os.path import join
from random import choice
import re
from environs import Env


def new_question():

    env = Env()
    env.read_env()

    path = env.str('PATH_QUIZ')

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
