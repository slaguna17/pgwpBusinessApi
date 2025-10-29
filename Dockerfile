# Imagen base oficial de AWS Lambda para Python 3.11 (Runtime API)
#FROM public.ecr.aws/lambda/python:3.11

# (Opcional) Dependencias del SO si tu backend lo requiere (certs, etc.)
# RUN yum -y update && yum -y install ca-certificates

#WORKDIR ${LAMBDA_TASK_ROOT}

# Copia e instala dependencias
#COPY requirements.txt .
#RUN python -m pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copia el código
#COPY app ${LAMBDA_TASK_ROOT}/app

# Handler de Lambda -> módulo.variable_función
# En este caso, 'app/handler.py' expone 'handler' (Mangum)
#CMD ["app.main.lambda_handler"]






FROM public.ecr.aws/lambda/python:3.11
WORKDIR ${LAMBDA_TASK_ROOT}

ENV PIP_ONLY_BINARY=:all:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # <-- sin --target

COPY app/ ./app
CMD ["app.main.lambda_handler"]
