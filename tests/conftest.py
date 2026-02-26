import os

# Set test env variables before app modules are imported
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")
os.environ.setdefault(
    "DATABASE_URL", "postgresql://admin:secret@localhost:5432/messenger"
)
