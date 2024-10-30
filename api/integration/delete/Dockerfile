FROM public.ecr.aws/lambda/python:3.10

COPY ./api/integration/delete/requirements.txt .

RUN pip install -r requirements.txt

COPY ./hooks/ ./hooks/

COPY ./entity/ ./entity/

COPY ./api/integration/delete/lambda_function.py ./lambda_function.py

CMD [ "lambda_function.handler" ]
