FROM python:3.10.1

WORKDIR /consumer

COPY ./requirements.txt /consumer/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /consumer/requirements.txt

COPY ./.env /consumer
COPY ./database /consumer/database
COPY ./consumer/consumer.py /consumer

CMD ["python", "/consumer/consumer.py"]
