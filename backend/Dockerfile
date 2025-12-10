# health-vault/backend/Dockerfile

# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your application code, models, and data files into the container
COPY main.py ./
COPY data_cleaner.py ./
COPY llm.py ./
COPY model_generator.py ./
COPY output.json ./
COPY medical_advanced_predictor.joblib ./
COPY medical_basic_predictor.joblib ./
# COPY .env ./
COPY uploads/ ./uploads/
COPY data.xlsx ./uploads/data.xlsx
CMD [ "main.handler" ]