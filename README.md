# ExpenseBot 💸

Telegram-бот для автоматичного трекінгу витрат через Apple Pay (iPhone Shortcuts).

## Можливості

- 📥 **Автоматичне збереження транзакцій** — через HTTP вебхук від iPhone Shortcuts
- 🔔 **Миттєві сповіщення** — бот надсилає повідомлення при кожній новій транзакції
- 🧾 **Перегляд транзакцій** — з пагінацією (кнопки ◀️ / ▶️)
- 📅 **Транзакції за тиждень/місяць** — фільтрація по датах
- 📊 **Статистика** — кількість, сума, середнє, максимум, мінімум за обраний період
- 🔒 **Приватний бот** — доступ лише для одного користувача (власника)

---

## Технічний стек

- **Python 3.12+**
- **aiogram 3.15+** — Telegram Bot Framework
- **aiohttp** — HTTP сервер для вебхуків
- **asyncpg** — асинхронний PostgreSQL драйвер
- **PostgreSQL** — база даних
- **Railway** — хостинг

---

## Структура проєкту

```
ExpenseBot/
├── bot/
│   ├── main.py              # Точка входу: запуск бота + aiohttp сервера
│   ├── config.py            # Конфігурація (env variables)
│   ├── handlers/
│   │   ├── start.py         # /start команда + головне меню
│   │   ├── transactions.py  # Перегляд транзакцій
│   │   └── stats.py         # Статистика витрат
│   ├── keyboards/
│   │   └── main.py          # Клавіатури (inline + reply)
│   ├── webhook/
│   │   └── server.py        # aiohttp сервер для даних від Shortcuts
│   ├── database/
│   │   ├── pool.py          # Connection pool (asyncpg)
│   │   └── transactions.py  # CRUD операції
│   └── services/
│       └── stats.py         # Логіка статистики
├── requirements.txt
├── Procfile
├── railway.toml
└── .env.example
```

---

## Налаштування та деплой

### 1. Створення Telegram бота

1. Відкрий [@BotFather](https://t.me/BotFather) в Telegram
2. Надішли `/newbot` і дотримуйся інструкцій
3. Отримай **BOT_TOKEN**
4. Дізнайся свій **Telegram User ID** через [@userinfobot](https://t.me/userinfobot)

### 2. Деплой на Railway

1. Зареєструйся на [Railway](https://railway.app)
2. Створи новий проєкт → **Deploy from GitHub repo**
3. Підключи цей репозиторій
4. Додай PostgreSQL сервіс: **New** → **Database** → **Add PostgreSQL**
5. Скопіюй `DATABASE_URL` з налаштувань PostgreSQL сервісу
6. Налаштуй змінні оточення (розділ **Variables**):

```env
BOT_TOKEN=<твій токен від BotFather>
DATABASE_URL=<URL з Railway PostgreSQL>
WEBHOOK_SECRET=<придумай секретний токен, наприклад: myS3cr3tT0k3n>
ALLOWED_USER_ID=<твій Telegram user ID>
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8080
```

7. Railway автоматично задеплоїть бота

### 3. Отримання URL вебхуку

Після деплою Railway надасть публічний URL у форматі:
```
https://your-app-name.up.railway.app
```

Вебхук ендпоінт буде доступний за адресою:
```
https://your-app-name.up.railway.app/api/transaction
```

---

## Налаштування iPhone Shortcuts (Автоматизація)

### Вимоги
- iPhone з iOS 17.5+
- Додаток **Shortcuts** (вбудований в iOS)

### Кроки налаштування

1. Відкрий **Shortcuts** → вкладка **Automation**
2. Натисни **+** → **New Automation**
3. Обери тригер **Transaction** (з'являється при прокрутці вниз)
4. Налаштування тригера:
   - **Any Card** або обери конкретну картку
   - **Any Amount** або встанови мінімальну суму
   - **Run Immediately** — вмикаємо, щоб не питало підтвердження кожного разу ✅
5. Додай дію **Get Contents of URL**:
   - **URL**: `https://your-app-name.up.railway.app/api/transaction`
   - **Method**: `POST`
   - **Request Body**: `JSON`
   - Додай поля:
     - `amount` → вибери **Shortcut Input** → **Amount**
     - `merchant` → вибери **Shortcut Input** → **Name**
     - `date` → вибери **Shortcut Input** → **Date** (форматуй як ISO 8601: `yyyy-MM-dd'T'HH:mm:ss`)
     - `token` → введи свій `WEBHOOK_SECRET` (той самий, що в Railway)
6. Збережи автоматизацію

### Приклад JSON, що надсилається від Shortcuts

```json
{
  "amount": 250.50,
  "merchant": "Silpo UAH",
  "date": "2026-04-07T14:30:00",
  "token": "myS3cr3tT0k3n"
}
```

---

## Використання бота

### Головне меню (Reply кнопки)

| Кнопка | Дія |
|--------|-----|
| 🧾 Транзакції | Останні транзакції з пагінацією |
| 📅 Цей тиждень | Транзакції з понеділка поточного тижня |
| 📆 Цей місяць | Транзакції за поточний місяць |
| 📊 Статистика | Вибір періоду для статистики |

### Сповіщення про нову транзакцію

```
✅ Нова транзакція!

💰 Сума: 250.50
🏪 Продавець: Silpo UAH
📅 Дата: 07.04.2026 14:30
```

### Команди (допоміжні)

- `/start` — відкрити головне меню
- `/transactions` — останні транзакції
- `/week` — транзакції за тиждень
- `/month` — транзакції за місяць
- `/stats` — статистика

---

## Локальний запуск (для розробки)

```bash
# Клонуй репозиторій
git clone https://github.com/th3ivn/ExpenseBot.git
cd ExpenseBot

# Встанови залежності
pip install -r requirements.txt

# Скопіюй і заповни змінні оточення
cp .env.example .env
# Відредагуй .env своїми значеннями

# Запусти бота
python -m bot.main
```

> **Примітка**: Для локального запуску потрібен PostgreSQL. Можна використати Docker:
> ```bash
> docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:16
> ```

---

## Вебхук API

### `POST /api/transaction`

Ендпоінт для прийому транзакцій від iPhone Shortcuts.

**Тіло запиту:**
```json
{
  "amount": 250.50,
  "merchant": "Назва продавця",
  "date": "2026-04-07T14:30:00",
  "token": "WEBHOOK_SECRET"
}
```

**Відповідь (успіх):**
```json
{
  "ok": true,
  "id": 42
}
```

**Коди відповідей:**
- `200` — транзакцію збережено
- `400` — невірний формат даних
- `401` — невірний токен
