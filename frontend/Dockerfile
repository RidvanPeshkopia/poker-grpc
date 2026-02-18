FROM python:3.9-slim
WORKDIR /app

# Install dependencies including gunicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

# Copy source code
COPY . .

# Copy proto and REGENERATE code to survive overwrite
COPY poker.proto .
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto

# Set environment
ENV PYTHONUNBUFFERED=1

# Use gunicorn as entrypoint
EXPOSE 8080
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]
