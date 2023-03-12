FROM python:3.11 as requirements-stage

WORKDIR /tmp


RUN pip install pipenv


COPY ./Pipfile /tmp/

RUN pipenv lock -r > requirements.txt

FROM python:3.11

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./main.py /code/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3111"]
