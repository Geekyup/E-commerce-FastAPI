# 🛒 FastAPI E-Commerce Шаблон

Чистый, готовый к production бэкенд-шаблон интернет-магазина на **FastAPI**, **SQLAlchemy** и **PostgreSQL**. Отличная отправная точка для любого e-commerce проекта.

---

## ✨ Возможности

- 🔐 **Аутентификация и авторизация** — JWT-токены с безопасным хешированием паролей
- 👤 **Управление пользователями** — Регистрация, вход, управление профилем
- 📦 **Каталог товаров** — CRUD для продуктов с поддержкой загрузки изображений
- 🛒 **Корзина** — Персональная корзина с управлением позициями
- 🗄️ **Миграции БД** — Версионирование схемы через Alembic
- ⚙️ **Админ-панель** — Встроенное управление суперпользователями
- 📁 **Загрузка файлов** — Обработка изображений товаров

---

## 🗂️ Структура проекта

```
├── main.py                  # Точка входа
├── alembic.ini              # Конфиг Alembic
├── .env                     # Переменные окружения (не коммитится)
│
├── app/
│   ├── api/                 # Роуты
│   │   ├── user.py
│   │   ├── product.py
│   │   └── cart.py
│   │
│   ├── models/              # ORM-модели SQLAlchemy
│   │   ├── user.py
│   │   ├── product.py
│   │   └── cart.py
│   │
│   ├── schemas/             # Pydantic-схемы
│   │   ├── user.py
│   │   ├── product.py
│   │   └── cart.py
│   │
│   ├── services/            # Бизнес-логика
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── upload.py
│   │
│   ├── core/                # Конфиг и безопасность
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/                  # Настройка базы данных
│   │   ├── session.py
│   │   ├── base.py
│   │   └── base_class.py
│   │
│   └── admin/               # Утилиты администратора
│       ├── views.py
│       └── createsuperuser.py
│
└── migrations/              # Файлы миграций Alembic
    └── versions/
```

---

## 🚀 Быстрый старт

### Требования

- Python 3.9+
- PostgreSQL

### Установка

1. **Клонировать репозиторий**
   ```bash
   git clone https://github.com/your-username/fastapi-ecommerce-template.git
   cd fastapi-ecommerce-template
   ```

2. **Создать и активировать виртуальное окружение**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Установить зависимости**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настроить переменные окружения**
   ```bash
   cp .env.example .env
   ```
   Заполните `.env` своими значениями:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
   SECRET_KEY=ваш-секретный-ключ
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Применить миграции**
   ```bash
   alembic upgrade head
   ```

6. **Создать суперпользователя** *(опционально)*
   ```bash
   python -m app.admin.createsuperuser
   ```

7. **Запустить сервер разработки**
   ```bash
   uvicorn main:app --reload
   ```

API будет доступно по адресу `http://localhost:8000`.  
Интерактивная документация: `http://localhost:8000/docs`

---

## 📡 Обзор API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/users/register` | Регистрация нового пользователя |
| `POST` | `/api/users/login` | Вход и получение JWT-токена |
| `GET` | `/api/users/me` | Получить профиль текущего пользователя |
| `GET` | `/api/products/` | Список всех товаров |
| `POST` | `/api/products/` | Создать товар *(админ)* |
| `GET` | `/api/products/{id}` | Получить товар по ID |
| `PUT` | `/api/products/{id}` | Обновить товар *(админ)* |
| `DELETE` | `/api/products/{id}` | Удалить товар *(админ)* |
| `GET` | `/api/cart/` | Получить корзину текущего пользователя |
| `POST` | `/api/cart/` | Добавить товар в корзину |
| `DELETE` | `/api/cart/{item_id}` | Удалить товар из корзины |

Полная интерактивная документация доступна через Swagger UI по адресу `/docs`.

---

## 🧪 Запуск тестов

```bash
pytest
```

---

## 🛠️ Технологии

| Слой | Технология |
|------|------------|
| Фреймворк | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| База данных | [PostgreSQL](https://www.postgresql.org/) |
| Миграции | [Alembic](https://alembic.sqlalchemy.org/) |
| Авторизация | JWT через [python-jose](https://github.com/mpdavis/python-jose) |
| Валидация | [Pydantic v2](https://docs.pydantic.dev/) |
| Сервер | [Uvicorn](https://www.uvicorn.org/) |

---

## 📄 Лицензия

Проект распространяется под лицензией MIT — подробнее см. файл [LICENSE](LICENSE).

---

## 🤝 Участие в разработке

Pull request'ы приветствуются! Для крупных изменений сначала откройте issue, чтобы обсудить предложение.

1. Сделайте форк репозитория
2. Создайте ветку для фичи (`git checkout -b feature/крутая-фича`)
3. Зафиксируйте изменения (`git commit -m 'Добавить крутую фичу'`)
4. Запушьте ветку (`git push origin feature/крутая-фича`)
5. Откройте Pull Request
