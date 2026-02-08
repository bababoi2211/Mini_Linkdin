

FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY requirement.txt .


RUN pip install --upgrade pip 

RUN pip install -r requirement.txt

COPY . .

# RUN python manage.py collectstatic --noinput

EXPOSE 8000


CMD ["gunicorn", "drf_proj.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8080","--workers","3"]
# CMD ["gunicorn", "drf_proj.wsgi", "--host","0.0.0.0","--port","8080"]
# CMD [ "python","manage.py","runserver","0.0.0.0:8080" ]
# CMD [ "uvicorn" , "drf_proj.asgi:application","--host","0.0.0.0","--port","8080","--reload" ]

