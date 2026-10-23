FROM apache/airflow:3.1.0-python3.12

COPY --chown=airflow:0 src /opt/project/src

# Dependências do projeto necessárias às tarefas da DAG.
# Instalar sem alterar a versão do Airflow fornecida pela imagem.
RUN pip install --no-cache-dir \
    'datasets>=3,<5' 'scikit-learn>=1.5,<2' 'joblib>=1.4,<2' 'numpy>=2,<3'c 'pandas>=2,<3'
