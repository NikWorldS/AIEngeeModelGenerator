FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_win.txt /tmp/requirements_win.txt

RUN pip install --no-cache-dir -r /tmp/requirements_win.txt
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

