from aiogram import Bot, Dispatcher, executor, types

# t.me/botForExam_bot
API_TOKEN = '5995846876:AAGJz3ioOTZw6aK9gaxg88gXBN9c6LizPKo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nОтправь мне любое сообщение, а я тебе обязательно отвечу.")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
