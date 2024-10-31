FROM public.ecr.aws/lambda/python:3.10

COPY ./api/history/list/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./api/history/list/func/ ./func/

COPY ./api/history/list/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
