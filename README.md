# ExpenseBot 💰

> Telegram Mini App для трекінгу витрат — аналог Brim (App Store), як Telegram WebApp.
> Все українською мовою, тільки для України, валюта ₴.

## Архітектура

Мікросервісна архітектура з 3 незалежних сервісів:

```
bot ──HTTP──> api ──SQL──> postgres
webapp ──HTTP──> api ──SQL──> postgres
Apple Pay webhook ──HTTP──> api
```

### Сервіси:
- **`bot/`** — Telegram Bot (aiogram 3.27+), обробляє команди, показує Mini App кнопку
- **`api/`** — REST API (FastAPI + SQLAlchemy 2.0 async + PostgreSQL), основна бізнес-логіка
- **`webapp/`** — Telegram Mini App (React 18 + TypeScript + Vite + Tailwind CSS)

## Технічний стек

| Шар | Технологія |
|-----|-----------|
| Bot | aiogram 3.27+, aiohttp |
| API | FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Database | PostgreSQL 16, asyncpg, Alembic |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| Infrastructure | Docker, docker-compose |

## Функціонал Mini App

- 📊 **Дашборд** — бюджетне кільце, 4 аналітичні картки, останні транзакції
- 📈 **Тренд витрат** — порівняння поточного місяця з середнім за 3 місяці
- 🍩 **Розбивка витрат** — donut chart по групах і категоріях
- 💰 **Норма збережень** — gauge діаграма + рівні (Базовий → Elite)
- 📋 **Заплановані витрати** — регулярні транзакції
- ➕ **Додати транзакцію** — Витрата / Дохід / Переказ
- ⚙️ **Налаштування** — бюджет, категорії, рахунки, теги, регулярні

## Швидкий старт (Docker)

### Вимоги
- Docker 24+
- docker-compose 2+

### Запуск

1. Скопіюй `.env.example` в `.env` і заповни змінні:
```bash
cp .env.example .env
```

2. Запусти всі сервіси:
```bash
docker-compose up -d
```

3. Застосуй міграції бази даних:
```bash
docker-compose exec api alembic -c api/database/migrations/alembic.ini upgrade head
```

4. Відкрий Mini App: `http://localhost:3000`
   API доступне: `http://localhost:8000/docs`

### Зупинити
```bash
docker-compose down
```

## Локальна розробка

### Backend API

```bash
cd /path/to/ExpenseBot
pip install -r api/requirements.txt

# Запуск
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/expensebot \
BOT_TOKEN=your_token \
WEBHOOK_SECRET=your_secret \
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API документація: http://localhost:8000/docs

### Bot

```bash
pip install -r requirements.txt

BOT_TOKEN=your_token \
DATABASE_URL=postgresql://user:pass@localhost/expensebot \
WEBHOOK_SECRET=your_secret \
ALLOWED_USER_ID=123456789 \
WEBAPP_URL=http://localhost:3000 \
python -m bot.main
```

### Frontend Mini App

```bash
cd webapp
cp .env.example .env
# Встанови VITE_API_URL=http://localhost:8000 в .env

npm install
npm run dev
```

Mini App буде доступний на http://localhost:5173

## Змінні середовища

| Змінна | Опис | Обов'язкова |
|--------|------|------------|
| `BOT_TOKEN` | Telegram Bot API token | ✅ |
| `DATABASE_URL` | PostgreSQL URL для бота (asyncpg) | ✅ |
| `WEBHOOK_SECRET` | Секрет для Apple Pay webhook | ✅ |
| `ALLOWED_USER_ID` | Telegram ID дозволеного користувача | ✅ |
| `WEBAPP_URL` | URL задеплоєного Mini App | ⚪ |
| `API_BASE_URL` | URL API сервісу (для бота) | ⚪ |
| `POSTGRES_USER` | PostgreSQL user (docker-compose) | ⚪ |
| `POSTGRES_PASSWORD` | PostgreSQL password (docker-compose) | ⚪ |
| `POSTGRES_DB` | PostgreSQL database name (docker-compose) | ⚪ |
| `VITE_API_URL` | API URL для frontend (webapp/.env) | ✅ webapp |

## API Endpoints

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/api/auth/validate` | Валідація Telegram initData |
| GET | `/api/transactions` | Список транзакцій |
| POST | `/api/transactions` | Створити транзакцію |
| PUT | `/api/transactions/{id}` | Оновити транзакцію |
| DELETE | `/api/transactions/{id}` | Видалити транзакцію |
| GET | `/api/categories` | Категорії |
| GET | `/api/accounts` | Рахунки з балансами |
| GET | `/api/budgets/current` | Поточний бюджет |
| GET | `/api/stats/summary` | Зведена статистика |
| GET | `/api/stats/trend` | Тренд витрат |
| GET | `/api/stats/breakdown` | Розбивка по категоріях |
| GET | `/api/stats/savings-rate` | Норма збережень |
| GET | `/api/settings` | Налаштування |
| POST | `/api/webhook/transaction` | Apple Pay webhook |

Повна документація API: `/docs` (Swagger UI)

## Міграції бази даних (Alembic)

```bash
# Застосувати всі міграції
alembic -c api/database/migrations/alembic.ini upgrade head

# Відкотити останню міграцію
alembic -c api/database/migrations/alembic.ini downgrade -1

# Переглянути статус
alembic -c api/database/migrations/alembic.ini current
```

## Deploy на Railway

Кожен сервіс деплоїться окремо:

1. **PostgreSQL** — Railway Postgres plugin
2. **API** — `Dockerfile.api`, env vars з Railway dashboard
3. **Bot** — `Dockerfile.bot`, env vars з Railway dashboard
4. **Webapp** — `Dockerfile.webapp` або Vercel/Netlify (static)

## Структура проекту

```
ExpenseBot/
├── bot/                    # Telegram Bot (aiogram)
│   ├── api_client.py       # HTTP client для API сервісу
│   ├── handlers/           # Обробники команд
│   ├── keyboards/          # Клавіатури
│   ├── database/           # Пряме підключення до БД (legacy)
│   └── services/           # Бізнес-логіка бота
│
├── api/                    # Backend API (FastAPI)
│   ├── auth/               # Telegram initData auth
│   ├── routers/            # API routes
│   ├── models/             # SQLAlchemy моделі
│   ├── schemas/            # Pydantic схеми
│   ├── services/           # Бізнес-логіка
│   └── database/           # DB сесія + Alembic міграції
│
├── webapp/                 # Telegram Mini App (React + TS + Vite)
│   ├── src/
│   │   ├── components/     # UI компоненти
│   │   ├── pages/          # Сторінки
│   │   ├── hooks/          # React hooks
│   │   ├── api/            # API клієнт
│   │   ├── types/          # TypeScript типи
│   │   └── utils/          # Утиліти
│   └── nginx.conf          # nginx конфіг для production
│
├── docker-compose.yml      # Локальна розробка
├── Dockerfile.bot
├── Dockerfile.api
├── Dockerfile.webapp
└── requirements.txt        # Python залежності бота
```
