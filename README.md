> 🇷🇺 [README в России](#) | [README.ru.md](./README.ru.md)

# 🛒 FastAPI E-Commerce Template

A clean, production-ready e-commerce backend template built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. Designed to be a solid starting point for any online store project.

---

## ✨ Features

- 🔐 **Authentication & Authorization** — JWT-based auth with secure password hashing
- 👤 **User Management** — Registration, login, profile management
- 📦 **Product Catalog** — CRUD for products with image upload support
- ⭐ **Product Reviews** — User reviews with 1-5 star ratings and average rating calculation
- 🛒 **Shopping Cart** — Per-user cart with item management
- 📦 **Orders** — Order management with status tracking
- 🗄️ **Database Migrations** — Alembic-powered schema versioning
- ⚙️ **Admin Panel** — Built-in superuser management with FastAdmin
- 📁 **File Uploads** — Product image handling

---

## 🗂️ Project Structure

```
├── main.py                  # App entry point
├── alembic.ini              # Alembic config
├── .env                     # Environment variables (not committed)
│
├── app/
│   ├── api/                 # Route handlers
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── category.py
│   │   └── review.py
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── category.py
│   │   └── review.py
│   │
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── category.py
│   │   └── review.py
│   │
│   ├── services/            # Business logic
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── category.py
│   │   ├── review.py
│   │   └── upload.py
│   │
│   ├── core/                # App config & security
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/                  # Database setup
│   │   ├── session.py
│   │   ├── base.py
│   │   └── base_class.py
│   │
│   └── admin/               # Admin utilities
│       ├── views.py
│       └── createsuperuser.py
│
└── migrations/              # Alembic migration files
    └── versions/
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/fastapi-ecommerce-template.git
   cd fastapi-ecommerce-template
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Fill in your values in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Apply database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Create a superuser** *(optional)*
   ```bash
   python -m app.admin.createsuperuser
   ```

7. **Run the development server**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/register` | Register a new user |
| `POST` | `/api/users/login` | Login and get JWT token |
| `GET` | `/api/users/me` | Get current user profile |
| `GET` | `/api/products/` | List all products |
| `POST` | `/api/products/` | Create a product *(admin)* |
| `GET` | `/api/products/{id}` | Get product by ID |
| `PUT` | `/api/products/{id}` | Update a product *(admin)* |
| `DELETE` | `/api/products/{id}` | Delete a product *(admin)* |
| `POST` | `/api/reviews/` | Create a product review |
| `GET` | `/api/reviews/product/{product_id}` | Get reviews for a product |
| `GET` | `/api/reviews/user/{user_id}` | Get reviews by a user |
| `PATCH` | `/api/reviews/{review_id}` | Update a review |
| `DELETE` | `/api/reviews/{review_id}` | Delete a review |
| `GET` | `/api/cart/` | Get current user's cart |
| `POST` | `/api/cart/` | Add item to cart |
| `DELETE` | `/api/cart/{item_id}` | Remove item from cart |

Full interactive documentation is available via Swagger UI at `/docs`.

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Database | [PostgreSQL](https://www.postgresql.org/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Auth | JWT via [python-jose](https://github.com/mpdavis/python-jose) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Server | [Uvicorn](https://www.uvicorn.org/) |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
