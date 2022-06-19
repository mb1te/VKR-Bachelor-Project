import os

API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('TOKEN')

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = int(os.getenv('PORT'))

START_MESSAGE = """\
    Для того чтобы воспользоваться моделью отправляйте запросы в следующем формате:

Вопрос
Вариант ответа 1
Вариант ответа 2
...
Вариант ответа N
"""
