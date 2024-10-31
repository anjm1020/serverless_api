FROM public.ecr.aws/lambda/python:3.10

COPY ./api/search/requirements.txt .

RUN pip install -r requirements.txt

COPY ./entity/ ./entity/

COPY ./hooks/ ./hooks/

COPY ./api/search/lambda_function.py .

CMD [ "lambda_function.handler" ]
