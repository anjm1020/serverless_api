FROM public.ecr.aws/lambda/python:3.10

COPY ./api/integration/google/callback/requirements.txt .

RUN pip install -r requirements.txt

COPY ./entity/ ./entity/

COPY ./hooks/ ./hooks/

COPY ./api/integration/google/callback/func/ ./func/

COPY ./api/integration/google/callback/.env ./.env

COPY ./api/integration/google/callback/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
