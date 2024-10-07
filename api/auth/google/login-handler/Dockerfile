FROM public.ecr.aws/lambda/python:3.10

COPY ./api/auth/google/login-handler/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/auth/google/login-handler/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
