from nltk.corpus import wordnet
from modules.translate import translate_ru, translate_en
from random import choice


words_list = ['Добрый день',
              'Беда не приходит одна',
              'Собака — друг человека',
              'Устами младенца глаголет истина',
              'Гадкий утенок',
              'Снежная королева',
              'Отцы и сыновья',
              'Старик и море',
              'Звездные войны',
              'Богатые тоже плачут'
              ]


def get_random_word():
    return choice(words_list)


def reverse_text(text):
    translated_text = translate_ru(text)
    words = translated_text.split()
    a_words = []
    for word in words:
        a_word = get_antonym(word)
        a_words.append(a_word)
    a_words[0] = a_words[0].title()
    a_text = translate_en(' '.join(a_words))
    return a_text


def get_antonym(word):
    antonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name().replace('_', ' '))
                return antonyms[0]
    return word
