FROM public.ecr.aws/lambda/python:3.10

COPY ./api/me/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/me/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
