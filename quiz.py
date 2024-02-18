from os import listdir
from os.path import join
from random import choice
import re


def get_quiz(quizs):

    question, answer = choice(quizs)

    answer = re.sub(r'\([^()]*\)|\[[^()]*\]', '', answer)
    answer = re.sub(r'[$|&|!|,|.|\"]', '', answer)
    answer = re.sub(r'[\d\.]', '', answer)
    answer = re.sub(r'^\s+|\s+$', '', answer)

    return question, answer


def load_quizs(path):

    filename = choice(listdir(path))

    with open(join(path, filename), 'r', encoding='KOI8-R') as f:
        text = f.read()

    questions = re.findall(r'Вопрос \d+:\s(.*?)\sОтвет', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.*?)\.\s\s', text)

    return list(zip(questions, answers))
