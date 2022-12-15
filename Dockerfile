FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt
RUN apt-get update -qq && apt-get install -y wait-for-it
COPY . /code/
RUN python3 manage.py collectstatic --noinput

