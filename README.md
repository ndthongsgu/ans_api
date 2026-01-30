# thay đổi model gõ câu lệnh
alembic revision --autogenerate -m "mô tả thay đổi"
alembic upgrade head

## ✅ Thiết lập CI & pre-commit (kiểm tra trước commit/push) 🔧

Đã thêm cấu hình sẵn:
- `.pre-commit-config.yaml` — format, lint, type-check trước commit/push
- `.github/workflows/ci.yml` — CI chạy trên GitHub Actions (push / PR)
- `requirements-dev.txt` — dependencies cho kiểm tra dev (pre-commit, pytest, mypy,...)

Hướng dẫn kích hoạt trên máy dev:

1) Cài dependencies dev:

```bash
pip install -r requirements-dev.txt
```

2) Cài pre-commit hook:

```bash
pre-commit install
# nếu muốn chạy pytest trước khi push
pre-commit install --hook-type pre-push
```

3) Kiểm tra nhanh (từ repo root):

```bash
# chạy tất cả hook (format/lint/typecheck)
pre-commit run --all-files

# chạy tests nếu có
pytest -q || true
```

> Lưu ý: CI trên GitHub sẽ chạy `pre-commit run --all-files`, `ruff`, `mypy` và `pytest` (nếu có folder `tests`).

---

