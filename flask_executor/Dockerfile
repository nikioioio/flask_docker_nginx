FROM python:3.7

RUN python -m pip install flask flask-cors gunicorn pandas openpyxl
RUN apt-get update
RUN apt-get install -y vim


WORKDIR /application

COPY . .


EXPOSE 5000

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "main_flask:app" ]

