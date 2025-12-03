FROM python:3.11

WORKDIR /app

COPY src/ /app/
COPY src/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--debug", "--host=0.0.0.0"]
