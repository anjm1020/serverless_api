FROM public.ecr.aws/lambda/python:3.10

COPY ./functions/jwt-validation-handler/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./functions/jwt-validation-handler/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]