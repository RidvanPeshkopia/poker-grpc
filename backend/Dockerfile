FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy proto file and generate code INSIDE the container
COPY poker.proto .
# Generate the gRPC files for the current directory
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto
COPY . .
EXPOSE 8080
CMD ["python", "server.py"]
