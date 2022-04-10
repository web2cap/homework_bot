import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv
from http import HTTPStatus
from telegram.error import TelegramError


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename="main.log",
    filemode="a",
    format="%(asctime)s, %(levelname)s, %(message)s, %(name)s",
)
logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f"Отправленно сообщение: {message}")
    except TelegramError as error:
        error_text = f"Ошибка отправки telegram сообщения: {error}"
        logger.error(error_text)
        raise RuntimeError(error_text)


def create_telegram_bot():
    "Создание телеграм бота."
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
    except Exception as error:
        error_text = f"Ошибка создания telegram bot: {error}"
        logger.error(error_text)
        raise ValueError(error_text)
    else:
        return bot


def get_api_answer(current_timestamp):
    """Делает запрос к ENDPOINT API-сервиса.
    В качестве параметра функция получает временную метку.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp
    params = {"from_date": timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)

    if homework_statuses.status_code == HTTPStatus.OK:
        logger.debug("Получен ответ со статусом 200 ОК")
        return homework_statuses.json()
    else:
        error_text = f"Ошибка http запроса: {homework_statuses.status_code}"
        logger.error(error_text)
        raise ValueError(error_text)


def check_response(response):
    """Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API
    Функция должна вернуть список домашних работ (он может быть и пустым),
    доступный в ответе API по ключу 'homeworks'.
    """
    if not isinstance(response, dict):
        raise TypeError(
            f"Тип ответа от api не dict. Неверный тип: {type(response)}"
        )
    assert "homeworks" in response, False
    assert isinstance(response["homeworks"], list)
    return response["homeworks"]


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент.
    Возвращает подготовленную для отправки в Telegram строку,
    содержащую один из вердиктов словаря HOMEWORK_STATUSE.
    """
    homework_name = homework["homework_name"]
    homework_status = homework["status"]

    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        error_text = f"Неизвестный статус: {homework_status}"
        raise ValueError(error_text)


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная окружения,
    функция должна вернуть False, иначе — True.
    """
    if not (
        len(str(PRACTICUM_TOKEN))
        and len(str(TELEGRAM_TOKEN))
        and TELEGRAM_CHAT_ID
    ):
        logger.critical("Ошибка проверки токенов.")
        return False
    return True


def get_last_update(homework):
    """Возвращает дату последнего апдейта."""
    return homework["date_updated"]


def main():
    """Основная логика работы бота."""
    try:
        if check_tokens() is False:
            raise ValueError("Ошибка проверки токенов.")
        bot = create_telegram_bot()
    except Exception as error:
        error_text = f"Ошибка инициализации: {error}"
        raise ValueError(error_text)

    current_timestamp = int(time.time())
    last_update = ""
    last_message = ""

    while True:
        try:
            message = ""
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)

            if homeworks is False:
                error_text = "Некоректные данные в ответе от API Яндекса"
                raise ValueError(error_text)

            if len(homeworks) > 0:
                current_update = get_last_update(homeworks[0])
                if current_update != last_update:
                    message = parse_status(homeworks[0])
                    last_update = current_update
                else:
                    logger.debug("Отсутствие в ответе новых статусов")
            else:
                message = "Нет работ для проверки"

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message)

        else:
            current_timestamp = int(time.time())

        if message != "" and message != last_message:
            send_message(bot, message)
            last_message = message

        time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
