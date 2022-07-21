"""Логгирование в телеграм.

1. Создать бот

Послать в канал https://t.me/botfather команду /newbot, записать токен

Например, konstantin_debug

2. Создать канал

В приложении телеграм, добавить бота в канал как администратора

Например, konstantin_debug

3. Узнать id канала

https://api.telegram.org/bot<YourBOTToken>/getUpdates

Цифры chat.id, например 1314183975 - послать от бота
Цифры sender_chat.id, например -1001555100085 - послать в канал


"""

from asyncio import sleep as asleep
from logging import Handler, LogRecord

from telegram import Bot, constants, error

from .settings import settings


class TelegramHandler(Handler):
    """Логгирование в телеграм."""

    def __init__(self: "TelegramHandler", tg: "Telegram") -> None:
        """Логгирование в телеграм.

        :param tg: бот для рассылки сообщений
        """
        super().__init__()
        self.__tg = tg

    def emit(self: "TelegramHandler", record: LogRecord) -> None:
        """Новое сообщение.

        :param record: сообщение
        """
        msg = self.format(record)
        self.__tg.add_message(msg)


class Telegram:
    """Рассылка сообщений в телеграм.

    Для работы необходимо создать задачу asyncio для функции self.task()
    """

    def __init__(self: "Telegram", token: str, chat_id: str) -> None:
        """Рассылка сообщений в телеграм.

        :param token: токен бота
        :param chat_id: id пользователя или канала (см описание модуля)
        """
        self.__bot = Bot(token=token)
        self.__chat_id = chat_id
        self.__messages: list[str] = []

    def add_message(self: "Telegram", text: str) -> None:
        """Добавить сообщение для рассылки.

        :param text: сообщение
        """
        self.__messages.append(text)

    async def task(self: "Telegram") -> None:
        """Задача для циклического выполнения."""
        while True:
            await self.__task()

    async def __task(self: "Telegram") -> None:
        if len(self.__messages) == 0:
            return await asleep(0)
        for msg in self.__messages:
            for char in "_*[]()~`>#+-=|{}.!":
                msg = msg.replace(char, "\\" + char)
            msg = "```\n" + msg + "\n```"
            try:
                await self.__bot.send_message(
                    chat_id=self.__chat_id,
                    text=msg,
                    parse_mode=constants.ParseMode.MARKDOWN_V2,
                )
            except error.NetworkError:
                await asleep(5)
            except error.RetryAfter:
                await asleep(5)
            finally:
                self.__messages.clear()
        return await asleep(0)


bot = Telegram(
    token=settings.telegram_token,
    chat_id=settings.telegram_chat_id,
)
