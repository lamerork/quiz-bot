from os import listdir
from os.path import join
from random import choice
import re


def main():

    path = 'quiz-questions'

    filename = choice(listdir(path))

    with open(join(path, filename), 'r', encoding='KOI8-R') as f:
        text = f.read()

    questions = re.findall(r'Вопрос \d+:\s(.*?)\s\sОтвет', text, re.DOTALL)
    answers = re.findall(r'Ответ:\s(.+)\s\s', text)

    questions_answers = dict(zip(questions, answers))

    for question, answer in questions_answers.items():
        print(f'{question}\n')
        print(f'{answer}\n\n')


    #print(files)


if __name__ == '__main__':
    main()

