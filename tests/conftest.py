import os

# Устанавливаем тестовый SECRET_KEY до импорта модулей приложения
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")
os.environ.setdefault(
    "DATABASE_URL", "postgresql://admin:secret@localhost:5432/messenger"
)
