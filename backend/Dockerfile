# health-vault/backend/Dockerfile

# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt ./

# Install the Python dependencies (add mangum and pydantic)
# Ensure your requirements.txt contains fastapi, uvicorn, pandas, scikit-learn, joblib, numpy, pydantic, mangum
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code and data files into the container
COPY main.py ./
COPY app.py ./
COPY data_cleaner.py ./
COPY llm.py ./
COPY model_generator.py ./
COPY output.json ./

# Set the command to run when the Lambda function is invoked
# It tells Lambda your handler is in 'app.py' and is named 'handler'
CMD [ "main.handler" ]
