FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "lambda_function.handler" ]
