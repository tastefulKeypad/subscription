# Структура проекта
```
subscription
├── db         - Содержит модели объектов для БД и файл инициализации БД.
├── endpoints  - Содержит endpoint'ы API.
└── schemas    - Содержит схемы объектов для валидации pydantic.
```
# Запланированные фичи
- [x] Ролевая модель (администратор/пользователь)
- [x] Система подписок с поддержкой промо-акций и возвратом средств
- [x] Scheduled tasks для автоматического списания/возврата средств
- [x] Реализация и интеграция фейковой платежной системы
- [x] Просмотр истории транзакций
- [x] Система уведомлений пользователей по почте

# Архитектура приложения (WIP)
![Архитектура приложения](https://github.com/tastefulKeypad/subscription/blob/main/app_architecture.svg)

# Порядок установки под Linux
```
git clone https://github.com/tastefulKeypad/subscription.git
cd subscription
python3 -m venv ./
source ./bin/activate
pip install -r requirements.txt
fastapi run main.py
```

Чтобы инициализировать бд пользователями и продуктами используйте endpoint 'populate_db' в default, после чего можно будет авторизироваться как администратор:

email: admin@example.com

pass:  admin 

Или как обычный пользователь:

email: user1@example.com 

pass:  user
