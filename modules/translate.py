import requests


api_key = 'trnsl.1.1.20190416T153618Z.98dd07147a00d262.de44998b11f26635808dba9425a7c3861743aa18'


def translate_ru(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    params = {
        'key': api_key,
        'text': text,
        'lang': 'ru-en'
    }

    response = requests.get(url, params)
    json = response.json()
    return json['text']


def translate_en(text):
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    params = {
        'key': api_key,
        'text': text,
        'lang': 'en-ru'
    }

    response = requests.get(url, params)
    json = response.json()
    return json['text']
