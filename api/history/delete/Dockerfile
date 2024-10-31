FROM public.ecr.aws/lambda/python:3.10

COPY ./api/history/delete/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/history/delete/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
