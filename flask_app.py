from flask import Flask, request
import logging
import json
from modules.translate import translate_en, translate_ru

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    handler = DialogHandler(request.json)
    handler.handle()

    return json.dumps(handler.get_res())


class DialogHandler:
    def __init__(self, request):
        self.response = AliceResponse()
        self.request = AliceRequest(request)

    def handle(self):
        if self.request.session_new():
            self.response.set_text('Привет, я - Алиса! Давай поиграем в перевёртыши!')
            self.response.set_suggest()
            return
        else:
            if self.request.text().lower() == 'помощь':
                self.response.set_text(
                    '''Я могу заменить все влова в предложении на антонимы.
                    Команда "Игра" - я буду загадывать перевёрнутые фразы, а ты постарайся их угадать.
                    Команда "Перевернуть" - введи команды, а в следующем сообщении предложение, и я его переверну.''')
                self.response.set_suggest()
                return

    def get_res(self):
        return self.response.get_res()


class AliceResponse:
    def __init__(self):
        self.res = {'session': request.json['session'],
                    'version': request.json['version'],
                    'response': {
                        'end_session': False
                    }
                    }

    def set_text(self, text):
        self.res['response']['text'] = text

    def add_text(self, text):
        self.res['response']['text'] += '\n{}'.format(text)

    def set_suggest(self):
        suggests = [{'title': 'Помощь', 'hide': True},
                    {'title': 'Игра', 'hide': True},
                    {'title': 'Перевернуть', 'hide': True}]
        self.res['response']['buttons'] = suggests

    def get_res(self):
        return self.res


class AliceRequest:
    def __init__(self, json_req):
        self.req = json_req

    def text(self):
        return self.req['request']['original_utterance']

    def get_user_id(self):
        return self.req['session']['user_id']

    def session_new(self):
        return self.req['session']['new']


if __name__ == '__main__':
    app.run()
