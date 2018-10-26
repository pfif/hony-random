from python:3-alpine

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY server.py tests.py ./

CMD python3 ./server.py
