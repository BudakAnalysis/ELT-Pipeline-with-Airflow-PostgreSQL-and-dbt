FROM apache/airflow:2.7.1

USER airflow

RUN pip install apache-airflow-providers-docker \ 
  && pip install apache-airflow-providers-http \ 
  %% pip install apache-airflow-providers-airbyte

