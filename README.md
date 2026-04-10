# ExpenseBot 💰

> Telegram Mini App для трекінгу витрат — аналог Brim (App Store), як Telegram WebApp.
> Все українською мовою, тільки для України, валюта ₴.

## Архітектура

Мікросервісна архітектура з 4 незалежних сервісів:

```
bot ──HTTP──> api ──SQL──> postgres
webapp ──HTTP──> api ──SQL──> postgres
Apple Pay webhook ──HTTP──> api ──SQL──> postgres
```

### Сервіси:
- **`bot/`** — Telegram Bot (aiogram 3.27+), обробляє команди через API
- **`api/`** — REST API (FastAPI + SQLAlchemy 2.0 async + PostgreSQL), вся бізнес-логіка
- **`webapp/`** — Telegram Mini App (React 18 + TypeScript + Vite + Tailwind CSS)
- **`postgres`** — Спільна база даних (єдине джерело правди)

**Важливо**: Bot і Mini App не взаємодіють напряму — обидва використовують `api` як єдине джерело правди.

## Технічний стек

| Шар | Технологія |
|-----|-----------|
| Bot | aiogram 3.27+, aiohttp, httpx |
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

Міграції застосовуються автоматично при старті API-контейнера.

3. Відкрий Mini App: `http://localhost:3000`
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
WEBHOOK_SECRET=your_secret \
ALLOWED_USER_ID=123456789 \
API_BASE_URL=http://localhost:8000 \
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

### PostgreSQL
| Змінна | Опис | За замовчуванням |
|--------|------|-----------------|
| `POSTGRES_USER` | PostgreSQL user | `expensebot` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `expensebot` |
| `POSTGRES_DB` | PostgreSQL database name | `expensebot` |

### API Service
| Змінна | Опис | Обов'язкова |
|--------|------|------------|
| `DATABASE_URL` | PostgreSQL URL (asyncpg) | ✅ |
| `BOT_TOKEN` | Telegram Bot API token | ✅ |
| `WEBHOOK_SECRET` | Секрет для Apple Pay webhook | ✅ |
| `API_HOST` | Хост сервера | `0.0.0.0` |
| `API_PORT` | Порт сервера | `8000` |

### Bot Service
| Змінна | Опис | Обов'язкова |
|--------|------|------------|
| `BOT_TOKEN` | Telegram Bot API token | ✅ |
| `WEBHOOK_SECRET` | Секрет для Apple Pay webhook | ✅ |
| `ALLOWED_USER_ID` | Telegram ID дозволеного користувача | ✅ |
| `API_BASE_URL` | URL API сервісу | `http://localhost:8000` |
| `WEBHOOK_HOST` | Хост webhook сервера | `0.0.0.0` |
| `WEBHOOK_PORT` | Порт webhook сервера | `8080` |
| `WEBAPP_URL` | URL задеплоєного Mini App | ⚪ |

### Webapp Service
| Змінна | Опис | Обов'язкова |
|--------|------|------------|
| `VITE_API_URL` | API URL для frontend | `/api` |

## API Endpoints

| Метод | Шлях | Опис |
|-------|------|------|
| POST | `/api/auth/validate` | Валідація Telegram initData |
| GET | `/api/transactions` | Список транзакцій |
| GET | `/api/transactions/count` | Кількість транзакцій |
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

## Авторизація

### Telegram WebApp (Mini App → API)
```
Authorization: Bearer <initData>
```
initData підписується і верифікується через HMAC-SHA256 з BOT_TOKEN.

### Service-to-Service (Bot → API)
```
X-Bot-Token: <BOT_TOKEN>
X-Telegram-User-Id: <telegram_id>
```

## Міграції бази даних (Alembic)

Міграції запускаються автоматично при старті API (через `api/entrypoint.sh`).

Ручне керування:
```bash
# Застосувати всі міграції
alembic -c api/database/migrations/alembic.ini upgrade head

# Відкотити останню міграцію
alembic -c api/database/migrations/alembic.ini downgrade -1

# Переглянути статус
alembic -c api/database/migrations/alembic.ini current
```

## Deploy на Railway

Один Railway project з 4 сервісами:

1. **PostgreSQL** — Railway Postgres plugin
2. **API** — `Dockerfile.api`, env vars: `DATABASE_URL`, `BOT_TOKEN`, `WEBHOOK_SECRET`
3. **Bot** — `Dockerfile.bot`, env vars: `BOT_TOKEN`, `WEBHOOK_SECRET`, `ALLOWED_USER_ID`, `API_BASE_URL`, `WEBAPP_URL`
4. **Webapp** — `Dockerfile.webapp`, build arg: `VITE_API_URL=https://your-api.railway.app`

## Структура проекту

```
ExpenseBot/
├── bot/                    # Telegram Bot (aiogram)
│   ├── api_client.py       # HTTP client для API сервісу
│   ├── handlers/           # Обробники команд і callback
│   ├── keyboards/          # Клавіатури
│   └── services/           # Бізнес-логіка бота
│
├── api/                    # Backend API (FastAPI)
│   ├── auth/               # Telegram initData auth
│   ├── routers/            # API routes
│   ├── models/             # SQLAlchemy моделі
│   ├── schemas/            # Pydantic схеми
│   ├── services/           # Бізнес-логіка
│   ├── database/           # DB сесія + Alembic міграції
│   └── entrypoint.sh       # Запуск: міграції + uvicorn
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

