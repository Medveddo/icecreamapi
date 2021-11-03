FROM python:3.10.0-slim

WORKDIR /app

COPY requirements/base.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt 

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]