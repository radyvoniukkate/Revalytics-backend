# Вибір образу з Python 3.10 + Debian Bullseye
FROM python:3.10-bullseye

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Створити робочу директорію
WORKDIR /app

# Копіювати файли проєкту
COPY . .

# Встановлення залежностей
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Відкрити порт для сервера
EXPOSE 8000

# Запуск FastAPI через Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]


