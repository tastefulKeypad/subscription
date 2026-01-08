# Запланированные фичи
- [x] Ролевая модель (администратор/пользователь)
- [ ] Система подписок с поддержкой промо-акций и возвратом средств
- [ ] Scheduled tasks для автоматического списания
- [ ] Реализация фейковой платежной системы
- [ ] Интеграция фейковой реализации платежной системы
- [ ] Просмотр истории транзакций
- [ ] Система уведомлений пользователей по почте

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
