import logging

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_polling

from AnswerModel import AnswerModel
import config


model = AnswerModel()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.message):
    await message.reply(config.START_MESSAGE)

@dp.message_handler()
async def answer(user_message: types.Message):
    message = user_message.text.split('\n')
    question, choices = message[0], message[1:]

    if len(message) < 2:
        await user_message.answer('Неправильный формат запроса')
        return

    model_answer = model.answer_question(question, choices)

    logging.info(f'{message=}{question=}\n{choices=}\n{model_answer=}')

    for ans in model_answer[::-1]:
        if ans != '':
            await user_message.answer(model_answer[1])
            return

    await user_message.answer('Не удалось однозначно определить ответ')

async def on_startup(dp):
    logging.info('STARTUP')
    await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    logging.info('SHUTDOWN')
    await bot.delete_webhook()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)