FROM python:3.9-slim
WORKDIR /app

# Copy files relative to the DOCKERFILE LOCATION (frontend/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use the LOCAL proto file
COPY poker.proto .
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto

# Copy the rest of the frontend code
COPY . .

EXPOSE 8080
CMD ["python", "app.py"]
