FROM public.ecr.aws/lambda/python:3.10

COPY ./functions/file-download-handler/requirements.txt .

RUN pip install -r requirements.txt

# COPY ./hooks/ ./hooks/

COPY ./functions/file-download-handler/func/ ./func/

COPY ./functions/file-download-handler/lambda_function.py .

CMD [ "lambda_function.handler" ]
