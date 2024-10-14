FROM public.ecr.aws/lambda/python:3.10

COPY ./functions/file-access-handler/requirements.txt .

RUN pip install -r requirements.txt

COPY ./entity/ ./entity/

COPY ./hooks/ ./hooks/

COPY ./functions/file-access-handler/func/ ./func/

COPY ./functions/file-access-handler/lambda_function.py .

CMD [ "lambda_function.handler" ]
