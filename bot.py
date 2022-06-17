import logging
from aiogram import Bot, Dispatcher, executor, types

from AnswerModel import AnswerModel
from config import START_MESSAGE, TOKEN

logging.basicConfig(level=logging.INFO)

model = AnswerModel()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.message):
    await message.reply(START_MESSAGE)

@dp.message_handler()
async def answer(user_message: types.Message):
    message = user_message.text.split('\n')
    question, choices = message[0], message[1:]

    if len(message) < 2:
        await user_message.answer('Неправильный формат запроса')
        return

    model_answer = model.answer_question(question, choices)
    await user_message.answer(model_answer[1])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)