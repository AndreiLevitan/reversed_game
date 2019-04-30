# Модуль для поиска антонимов к словам
from nltk.corpus import wordnet
# Модуль для перевода Яндекс.Переводчиком с английского
# на русский и с русского на английский
from modules.translate import translate_ru, translate_en
from random import choice


# Список словосочетаний для игры Алисы
# Включает сочетания, названия книг, пословицы
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


# Выбирает случайное словосочетание из words_list
def get_random_word():
    return choice(words_list)


# Переворачивает текст
def reverse_text(text):
    # Сначала переводим его на английский
    # так как wordnet работает только с английским языком
    translated_text = translate_ru(text)

    # Разделяем предложение на слова
    words = translated_text.split()

    # Список антонимов
    a_words = []
    for word in words:
        a_word = get_antonym(word)  # Получаем антони слова
        a_words.append(a_word)  # Добавляем его к списку антонимов
    a_words[0] = a_words[0].title()  # Устанавливаем первое слово заглавным
    a_text = translate_en(' '.join(a_words))  # Объединяем list в str
    return a_text


def get_antonym(word):
    # Создаём список антонимов
    antonyms = []
    # Проходим по списку синсетов данного слова
    for syn in wordnet.synsets(word):
        # Проходим по леммам синсета
        for l in syn.lemmas():
            # Если лемма имеет антоним
            if l.antonyms():
                # Добавляем его в словарь антонимов, заменяя "_" на пробелы
                antonyms.append(l.antonyms()[0].name().replace('_', ' '))
                return antonyms[0]
    return word
