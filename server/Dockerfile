# Вибір образу з Python 3.10
FROM python:3.10

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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
