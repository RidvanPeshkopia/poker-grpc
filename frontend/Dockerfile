FROM python:3.9-slim
WORKDIR /app

# Copy files relative to the REPOSITORY ROOT (Standard Cloud Build Context)
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use the original proto file from protos/ folder
COPY protos/poker.proto .
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto

# Copy the rest of the frontend code
COPY frontend/ .

EXPOSE 8080
CMD ["python", "app.py"]
