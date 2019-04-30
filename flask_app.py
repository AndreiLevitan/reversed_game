from flask import Flask, request
import logging
import json
from modules.wordw import reverse_text, get_random_word

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
        user_id = self.request.get_user_id()
        if self.request.session_new():
            self.response.set_text('Привет, я - Алиса! Давай поиграем в перевёртыши!')
            self.response.set_suggest_start()
            sessionStorage[user_id] = {
                'reversing': False,
                'game': False,
                'answer': None,
                'guess': False
            }
            return
        else:
            if self.request.text().lower() == 'помощь':
                self.response.set_text(
                    '''Я могу заменить все слова в предложении на антонимы.
                    Команда "Игра" - я буду загадывать перевёрнутые фразы, а ты постарайся их угадать.
                    Команда "Перевернуть" - введи команду, а в следующем сообщении предложение, и я его переверну.
                    (Могут быть искажения)''')
                self.response.set_suggest_start()
                return
            elif self.request.text().lower() == 'перевернуть':
                self.response.set_text('Введи текст и я его переверну.')
                sessionStorage[user_id]['reversing'] = True
                sessionStorage[user_id]['game'] = False
                return
            elif sessionStorage[user_id]['reversing']:
                reversed_text = reverse_text(self.request.text())
                self.response.set_text(reversed_text)
                sessionStorage[user_id]['reversing'] = False
                self.response.set_suggest_start()
                return
            elif self.request.text().lower() == 'игра':
                self.response.set_text('Начинается игра, для остановки напиши "Стоп"')
                sessionStorage[user_id]['reversing'] = False
                sessionStorage[user_id]['game'] = True
                reversed_word = self.get_word(user_id)
                self.response.add_text('"{}" - это...'.format(reversed_word))
                self.response.set_suggest_stop()
                return
            elif sessionStorage[user_id]['game'] and not sessionStorage[user_id]['guess']:
                word = self.request.text().lower()
                if word == sessionStorage[user_id]['answer']:
                    self.response.set_text('Поздравляю, ты угадал! Продолжить игру?')
                    self.response.set_suggest_next()
                    sessionStorage[user_id]['guess'] = True
                    return
                elif self.request.text().lower() == 'стоп':
                    sessionStorage[user_id]['game'] = False
                    sessionStorage[user_id]['answer'] = None
                    sessionStorage[user_id]['guess'] = False
                    self.response.set_text('Конец игры!')
                    self.response.set_suggest_start()
                    return
                else:
                    self.response.set_text('Не-а, попробуй ещё')
                    self.response.set_suggest_stop()
                    return
            elif sessionStorage[user_id]['game']:
                if self.request.text().lower() == 'да' and sessionStorage[user_id]['guess']:
                    sessionStorage[user_id]['guess'] = False
                    reversed_word = self.get_word(user_id)
                    self.response.set_text('Продолжаем, "{}" - это...'.format(reversed_word))
                    self.response.set_suggest_stop()
                    return
                elif self.request.text().lower() == 'стоп':
                    sessionStorage[user_id]['game'] = False
                    sessionStorage[user_id]['answer'] = None
                    sessionStorage[user_id]['guess'] = False
                    self.response.set_text('Конец игры!')
                    self.response.set_suggest_start()
                    return

        self.response.set_text('Не поняла команды, введи "Помощь"')
        return

    def get_res(self):
        return self.response.get_res()

    def get_word(self, user_id):
        word = get_random_word().lower()
        logging.info('Word: %r', word)
        reversed_word = reverse_text(word)
        sessionStorage[user_id]['answer'] = word
        return reversed_word


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

    def set_suggest_start(self):
        suggests = [{'title': 'Помощь', 'hide': True},
                    {'title': 'Игра', 'hide': True},
                    {'title': 'Перевернуть', 'hide': True}]
        self.res['response']['buttons'] = suggests

    def set_suggest_next(self):
        suggests = [{'title': 'Да', 'hide': True},
                    {'title': 'Стоп', 'hide': True}]
        self.res['response']['buttons'] = suggests

    def set_suggest_stop(self):
        suggests = [{'title': 'Стоп', 'hide': True}]
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
