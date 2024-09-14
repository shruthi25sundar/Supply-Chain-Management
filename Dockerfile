FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY Data/supplier_contracts_dataset.csv Data/supplier_contracts_dataset.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY Supplier_Performance_Analysis .

EXPOSE 5000

CMD gunicorn --bind 0.0.0.0:5000 app:app