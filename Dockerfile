FROM python:3.7
RUN pip install fastapi uvicorn
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
