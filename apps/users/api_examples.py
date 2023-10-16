import requests

# Регистрация пользователя
registration_data = {
    "email": "user@example.com",
    "password": "password123",
    # ... Другие поля ...
}
registration_response = requests.post("http://127.0.0.1:8000/api/v1/users/sign_up/", json=registration_data)

# Авторизация пользователя
# Авторизация пользователя
login_data = {
    "email": "user@example.com",
    "password": "password123",
}
login_response = requests.post("http://127.0.0.1:8000/api/sign_in/", data=login_data)
login_response_data = login_response.json()

jwt_token = login_response_data.get("access", "")  # Используйте "access" вместо "token"

# Добавление токена к заголовкам запроса
headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# Делаем GET-запрос к защищенной конечной точке API с использованием токена
# protected_response = requests.get("http://127.0.0.1:8000/api/v1/event/create/", headers=headers)
# print(protected_response.text)
