import requests


class TelegramBot:
    def __init__(self, token):
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, message_text):
        url = f"{self.base_url}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message_text,
            "parse_mode": "MarkdownV2"
        }
        response = requests.post(url, json=params)
        self._handle_response(response)

    def get_chat_info(self, chat_id):
        url = f"{self.base_url}/getChat"
        params = {
            "chat_id": chat_id
        }
        response = requests.get(url, params=params)
        self._handle_response(response)

    def get_updates(self):
        url = f"{self.base_url}/getUpdates"
        response = requests.get(url)
        self._handle_response(response)

    def _handle_response(self, response):
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                print("Запрос успешно выполнен.")
                # Обработка полученных данных, если необходимо
            else:
                print(f"Ошибка: {data['description']}")
        else:
            print("Произошла ошибка при выполнении запроса.")