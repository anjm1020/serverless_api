FROM public.ecr.aws/lambda/python:3.10

COPY ./api/auth/google/callback/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/auth/google/callback/func/ ./func/

COPY ./api/auth/google/callback/.env ./.env

COPY ./api/auth/google/callback/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
