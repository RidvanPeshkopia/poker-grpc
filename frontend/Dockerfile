FROM python:3.9-slim
WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL source code (including app.py and potentially stale pb2 files)
COPY . .

# Copy proto file just to be sure it's fresh
COPY poker.proto .

# FORCE RE-GENERATION of gRPC files *AFTER* copying source code
# This ensures that any stale local files are overwritten by fresh ones
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto

# Set explicit python buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "app.py"]
