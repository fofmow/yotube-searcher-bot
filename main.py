import hashlib
import logging
from os import environ
from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputMessageContent, InputFile
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from searcher import get_videos_by_query


bot = Bot(environ.get("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def greeting(message: Message):
    await message.answer("<b>Привет! Введи ключевые слова для поиска на YouTube и я "
                         "отправлю в чат первые 3 найденные видео  🥷🏻</b>")

    await message.answer_photo(
        InputFile("example.png"),
        caption="<b>P.S. Чтобы вызвать бота из другого чата используйте конструкцию 👆🏻</b>"
    )


@dp.message_handler(content_types=["text"])
async def send_videos(message: Message):
    if message.text.startswith("https://www.youtube.com/"):
        # в случае использования inline-запроса непосредственно в чате с ботом
        return

    videos = await get_videos_by_query(message.text)

    await message.answer("<b>По Вашему запросу получены следующие результаты ⚡️️</b>")
    for v in videos:
        view_buttons = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Смотреть", url=v.url),
            InlineKeyboardButton("Скачать", callback_data=f"download::{v.url}"),
        )
        await message.answer_photo(
            photo=v.logo_url,
            caption=f"<b>{v.title}</b>\n\n<i>Продолжительность: {v.duration}\n"
                    f"Канал: {v.channel}\nПросмотров: {v.views}\nОпубликовано: {v.publish_time}</i>",
            reply_markup=view_buttons
        )


@dp.callback_query_handler(text_contains="download")
async def download_video(call: CallbackQuery):
    video_url = call.data.split("::")[-1]
    # для скачивания видео можете использовать pytube ...

    await call.answer("Возможно, функционал скачивания видео в самом лучшем "
                      "качестве появится в платной версии бота", show_alert=True)


@dp.inline_handler()
async def inline_handler(query: InlineQuery):
    videos = [InlineQueryResultArticle(
        id=hashlib.md5(video.title.encode()).hexdigest(),
        title=video.title,
        url=video.url,
        thumb_url=video.logo_url,
        input_message_content=InputMessageContent(
            message_text=video.url
        )
    ) for video in await get_videos_by_query(query.query, max_results=5)]

    await query.answer(
        results=videos,
        cache_time=1,
        switch_pm_text="Перейти в Бота",
        switch_pm_parameter="go"
    )


logging.basicConfig(level=logging.INFO, filename="debug.log")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
