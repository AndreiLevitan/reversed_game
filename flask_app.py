from flask import Flask, request
import logging
import json
from modules.translate import translate


app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handler = DialogHandler(response, request.json)
    handler.handle()

    logging.info('Request: %r', response)

    return json.dumps(handler.get_res())


class DialogHandler:
    def __init__(self, request, response):
        self.response = AliceResponse(response)
        self.request = AliceRequest(request)

    def handle(self):
        user_id = self.request.get_user_id()

        if self.request.session_new():
            self.response.set_text('Привет, я - Алиса! Давай поиграем в перевёртыши!')
            return

    def get_res(self):
        return self.response.get_res()


class AliceResponse:
    def __init__(self, json_res):
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

    def get_res(self):
        return self.res


class AliceRequest:
    def __init__(self, json_req):
        self.req = json_req

    def get_user_id(self):
        return self.req['session']['user_id']

    def session_new(self):
        return self.req['session']['new']


if __name__ == '__main__':
    app.run()
