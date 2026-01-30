# Hướng dẫn khởi chạy và phát triển project 🚀

Tài liệu ngắn gọn giúp bạn thiết lập môi trường, chạy local, thao tác migration và kiểm tra nhanh.

---

## ⚙️ Chuẩn bị môi trường

1. Tạo và kích hoạt virtualenv (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Cài dependencies:

```bash
pip install -r requirements.txt
```

3. Tạo file cấu hình môi trường `.env` ở root (ví dụ):

```ini
# .env
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🗄 Database & Migration (alembic)

- Tạo migration tự động (sau khi thay model):

```bash
alembic revision --autogenerate -m "mô tả thay đổi"
```

- Áp migration lên DB:

```bash
alembic upgrade head
```

---

## ▶️ Chạy server (development)

- Chạy bằng Uvicorn (reload khi phát triển):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Điểm vào API: `http://127.0.0.1:8000` — ví dụ: `GET /` trả về `{"message":"Hello World"}`
- Tài liệu API (Swagger): `http://127.0.0.1:8000/docs`

---

## ✅ Kiểm tra & CI

- Cài pre-commit hooks (format, lint, type-check):

```bash
pre-commit install
# Nếu muốn chạy pytest trước khi push
pre-commit install --hook-type pre-push
```

- Chạy toàn bộ hooks thủ công:

```bash
pre-commit run --all-files
```

- Chạy tests:

```bash
pytest -q
```

> Lưu ý: pipeline CI (GitHub Actions) đã cấu hình sẵn để chạy `pre-commit`, `ruff`, `mypy` và `pytest`.

---

## 🔧 Các lệnh thường dùng

- Cài dep: `pip install -r requirements.txt`
- Tạo migration: `alembic revision --autogenerate -m "..."`
- Áp migration: `alembic upgrade head`
- Chạy server: `uvicorn main:app --reload`
- Chạy tests: `pytest -q`

---

## 💡 Ghi chú

- File cấu hình chính nằm ở `core/config.py` (đọc từ `.env`).
- DB connection lấy từ `DATABASE_URL` (mặc định sử dụng MySQL). Nếu dùng SQLite, chỉnh biến tương ứng.
- Nếu cần hỗ trợ thiết lập DB (MySQL) cục bộ, cho biết hệ điều hành và mình sẽ thêm hướng dẫn cụ thể.

---

Cần tôi bổ sung phần nào (ví dụ: hướng dẫn chạy trên Docker, CI chi tiết, hoặc cấu hình dev database)?

