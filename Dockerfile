FROM python:3.12-slim

WORKDIR /central_junior

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000

#CMD python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000