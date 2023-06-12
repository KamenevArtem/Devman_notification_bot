import os
import requests
import telegram

from dotenv import load_dotenv


load_dotenv()
dev_access_token = os.environ['DEVMAN_API_TOKEN']
bot_token = os.environ['TG_BOT_TOKEN']
chat_id = os.environ['CHAT_ID']
bot = telegram.Bot(token=bot_token)


def get_user_reviews(headers):
    url = 'https://dvmn.org/api/user_reviews/'
    reviews_response = requests.get(url, headers=headers)
    reviews_response.raise_for_status()
    return reviews_response.json()


def long_polling_reviews(headers):
    url = 'https://dvmn.org/api/long_polling/'
    long_polling_response = requests.get(
        url,
        headers=headers,
    )
    long_polling_response.raise_for_status()
    response = long_polling_response.json()
    if 'timestamp_to_request' in response:
        params = {
            'timestamp': {response['timestamp_to_request']}
        }
        timestamp_response = requests.get(
            url,
            headers=headers,
            params=params
        )
        timestamp_response.raise_for_status()
        response = timestamp_response.json()
    if response['status'] == 'found':
        notification_text = 'У Вас проверили работу, отправляем уведомление о проверке работ.'
        mistakes_notification_text = 'К сожалению в работе нашлись ошибки!'
        approved_text = 'Преподавателю все понравилось, можно приступать к следующему уроку'
        lesson_response = response['new_attempts']
        last_lesson_description = lesson_response[0]
        lesson_url = last_lesson_description['lesson_url']
        if last_lesson_description['is_negative']:
            bot.send_message(
                chat_id=chat_id,
                text=f'{notification_text}\n{mistakes_notification_text}\n'
                f'Ссылка на урок: {lesson_url}'
                )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=f'{notification_text}\n{approved_text}'
                )
    return response


def main():
    headers = {
        'Authorization': f'Token {dev_access_token}'
    }
    get_user_reviews(headers)
    while True:
        try:
            long_polling_reviews(headers)
        except (requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectionError):
            pass


if __name__ == '__main__':
    main()