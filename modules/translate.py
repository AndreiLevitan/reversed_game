import requests


# API ключ к сервису ЯндексюПереводчика
api_key = 'trnsl.1.1.20190416T153618Z.98dd07147a00d262.de44998b11f26635808dba9425a7c3861743aa18'


# Перевод русского текста на английский
def translate_ru(text):
    # Сервер API Яндекс.Переводчика
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    # Параметры запроса на сервер
    params = {
        'key': api_key,
        'text': text,
        'lang': 'ru-en'
    }
    # Создаем ответ из запроса с параметрами
    response = requests.get(url, params)
    json = response.json()
    # Возвращаем str перевода text
    return json['text'][0]


# Перевод английского текста на русский
def translate_en(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    params = {
        'key': api_key,
        'text': text,
        'lang': 'en-ru'
    }

    response = requests.get(url, params)
    json = response.json()
    return json['text'][0]
