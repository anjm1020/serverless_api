FROM public.ecr.aws/lambda/python:3.10

COPY ./api/auth/login/callback/requirements.txt .

RUN pip install -r requirements.txt

COPY ./entity/ ./entity/

COPY ./hooks/ ./hooks/

COPY ./api/auth/login/callback/func/ ./func/

COPY ./api/auth/login/callback/.env ./.env

COPY ./api/auth/login/callback/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
