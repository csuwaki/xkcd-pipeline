FROM apache/airflow:2.10.5

USER root

RUN pip install --upgrade pip

RUN pip install --no-cache-dir \
    dbt-core==1.9.4 \
    dbt-postgres==1.9.4

USER airflow