from flask import Flask, request
import logging
import json
# модуль для работы с перевёртышами
from modules.wordw import reverse_text, get_random_word


# Этот навык для Алисы является адаптацией игры "Перевертыши"
# В этой игре участнику необходимо отгадать перевёрнутое загадонное предложение или словосочетание ведущим
# В навыке ведущий - Алиса, а игрок - пользователь


# Создаём приложение Flask для обработки навыка
app = Flask(__name__)

# Настроиваем логирование
logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

# Словарь хранения данных пользователей
sessionStorage = {}


# Про отправке POST-запроса на /post запускаем handler
@app.route('/post', methods=['POST'])
def main():
    # Логируем request пользователя
    logging.info('Request: %r', request.json)

    # Создаём экземпляр класса DialogHandler, передаём в него request
    handler = DialogHandler(request.json)
    # Запускаем алгоритм обработки диалога
    handler.handle()

    # Возвращаем json-словарь response обработчика handler
    return json.dumps(handler.get_res())


# Основной класс обработки диалога пользователя и Алисы
# Взаимодействует с классами AliceResponse и AliceRequest
# которые необходимы для более удобного обращение с response и request пользоветеля
# и представляют собой обёртку над response и request соответственно
class DialogHandler:
    def __init__(self, request):
        # Инициализируем экземпляр класса-обёртки над response
        self.response = AliceResponse()
        # Инициализируем экземпляр класса-обёртки над response
        self.request = AliceRequest(request)

    # основной алгоритм обработки диалога и взаимодействия пользователя и Алисы
    def handle(self):
        user_id = self.request.get_user_id()
        # Если пользователь только что начал сессию,
        # то отправляем ему начальное сообщение
        if self.request.session_new():
            self.response.set_text('Привет, я - Алиса! Давай поиграем в перевёртыши!')
            # Выводим начальные вспомогательные кнопки
            self.response.set_suggest_start()
            # Инициализируем основные перевменные sessionStorage от user_id
            sessionStorage[user_id] = {
                'reversing': False,  # Ввёл ли команду "Перевернуть" пользователь
                'game': False,  # Играет ли сейчас пользователь
                'answer': None,  # Верный ответ
                'guess': False  # Угадал ли пользователь ответ
            }
            return
        else:
            # Если пользователь ввёл "Помощь"
            # то предоставляем ему сведения о навыке
            if self.request.text().lower() == 'помощь':
                self.response.set_text(
                    '''Я могу заменить все слова в предложении на антонимы.
                    Команда "Игра" - я буду загадывать перевёрнутые фразы, а ты постарайся их угадать.
                    Команда "Перевернуть" - введи команду, а в следующем сообщении предложение, и я его переверну.
                    (Могут быть искажения)''')

                # Выводим начальные кнопки помощи
                self.response.set_suggest_start()
                return
            # Если пользователь ввёл "Перевернуть"
            # то запускаем алгоритм переворачивания
            elif self.request.text().lower() == 'перевернуть':
                self.response.set_text('Введи текст и я его переверну.')
                sessionStorage[user_id]['reversing'] = True
                sessionStorage[user_id]['game'] = False
                return
            # Если пользователь уже переворачивает
            # то отправляем ему перевёрнутый запрос
            elif sessionStorage[user_id]['reversing']:
                reversed_text = reverse_text(self.request.text())
                self.response.set_text(reversed_text)
                sessionStorage[user_id]['reversing'] = False
                self.response.set_suggest_start()
                return
            # Если пользователь ввёл "Игра"
            # то начинаем игру
            elif self.request.text().lower() == 'игра':
                self.response.set_text('Начинается игра, для остановки напиши "Стоп"')
                sessionStorage[user_id]['reversing'] = False
                sessionStorage[user_id]['game'] = True
                reversed_word = self.get_word(user_id)
                self.response.add_text('"{}" - это...'.format(reversed_word))
                self.response.set_suggest_stop()
                return
            # Если пользователь ещё играет, но не отгадал ответ
            elif sessionStorage[user_id]['game'] and not sessionStorage[user_id]['guess']:
                word = self.request.text().lower()
                # Если пользователь угадал перевёртыш
                # то выводим сообщение поздравления
                # и запрос продолжения игры
                if word == sessionStorage[user_id]['answer']:
                    self.response.set_text('Поздравляю, ты угадал! Продолжить игру?')
                    self.response.set_suggest_next()
                    sessionStorage[user_id]['guess'] = True
                    return
                # Если же он ввёл "Стоп"
                # то останавливаем игру
                elif self.request.text().lower() == 'стоп':
                    sessionStorage[user_id]['game'] = False
                    sessionStorage[user_id]['answer'] = None
                    sessionStorage[user_id]['guess'] = False
                    self.response.set_text('Конец игры!')
                    self.response.set_suggest_start()
                    return
                # Если же он не угадал слово
                # то выводим соответствующее сообщение
                else:
                    self.response.set_text('Не-а, попробуй ещё')
                    self.response.set_suggest_stop()
                    return
            # Если пользователь играет
            elif sessionStorage[user_id]['game']:
                # уже угадал слово и ввёл "да"
                # то продолжаем игру
                if self.request.text().lower() == 'да' and sessionStorage[user_id]['guess']:
                    sessionStorage[user_id]['guess'] = False
                    reversed_word = self.get_word(user_id)
                    self.response.set_text('Продолжаем, "{}" - это...'.format(reversed_word))
                    self.response.set_suggest_stop()
                    return
                # иначе завершаем игру
                elif self.request.text().lower() == 'стоп':
                    sessionStorage[user_id]['game'] = False
                    sessionStorage[user_id]['answer'] = None
                    sessionStorage[user_id]['guess'] = False
                    self.response.set_text('Конец игры!')
                    self.response.set_suggest_start()
                    return

        # Если пользователь ввёл некоретную команду
        # то выводим соответствующее сообщение
        self.response.set_text('Не поняла команды, введи "Помощь"')
        return

    # Метод возвращения response обратно в main метод приложения Flask
    def get_res(self):
        return self.response.get_res()

    # Метод получение случайного слова из wordw
    # и запись его в sessionStorage
    def get_word(self, user_id):
        word = get_random_word().lower()
        logging.info('Word: %r', word)
        reversed_word = reverse_text(word)
        sessionStorage[user_id]['answer'] = word
        return reversed_word


# Класс-обёртка над response Алисы
class AliceResponse:
    def __init__(self):
        self.res = {'session': request.json['session'],
                    'version': request.json['version'],
                    'response': {
                        'end_session': False
                    }
                    }

    # Устанавливаем текст в response на text
    def set_text(self, text):
        self.res['response']['text'] = text

    # Добавляем к тексту reponse текст text с новой строки
    def add_text(self, text):
        self.res['response']['text'] += '\n{}'.format(text)

    # Установка кнопок главного меню
    def set_suggest_start(self):
        suggests = [{'title': 'Помощь', 'hide': True},
                    {'title': 'Игра', 'hide': True},
                    {'title': 'Перевернуть', 'hide': True}]
        self.res['response']['buttons'] = suggests

    # Установка кнопок для продолжения игры
    def set_suggest_next(self):
        suggests = [{'title': 'Да', 'hide': True},
                    {'title': 'Стоп', 'hide': True}]
        self.res['response']['buttons'] = suggests

    # Установка кнопки остановки игры
    def set_suggest_stop(self):
        suggests = [{'title': 'Стоп', 'hide': True}]
        self.res['response']['buttons'] = suggests

    # Метод возвращения response
    def get_res(self):
        return self.res


# Класс-обёртка над request пользователя
class AliceRequest:
    def __init__(self, json_req):
        self.req = json_req

    # Возвращаем текст пользователя
    def text(self):
        return self.req['request']['original_utterance']

    # Возвращаеи id пользователя
    def get_user_id(self):
        return self.req['session']['user_id']

    # Возращаем значение, новая ли сессия
    def session_new(self):
        return self.req['session']['new']


# Запуск сервера
if __name__ == '__main__':
    app.run()
