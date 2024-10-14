FROM public.ecr.aws/lambda/python:3.10

COPY ./functions/file-retrieve-handler/requirements.txt .

RUN pip install -r requirements.txt

COPY ./entity/ ./entity/

COPY ./hooks/ ./hooks/

COPY ./functions/file-retrieve-handler/func/ ./func/

COPY ./functions/file-retrieve-handler/lambda_function.py .

CMD [ "lambda_function.handler" ]
