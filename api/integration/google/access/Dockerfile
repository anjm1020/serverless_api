FROM public.ecr.aws/lambda/python:3.10

COPY ./api/integration/google/access/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/integration/google/access/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
