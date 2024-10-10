FROM public.ecr.aws/lambda/python:3.10

COPY ./functions/file-listing-handler/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./functions/file-listing-handler/func/ ./func/

COPY ./functions/file-listing-handler/lambda_function.py .

CMD [ "lambda_function.handler" ]
