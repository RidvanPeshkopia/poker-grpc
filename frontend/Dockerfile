FROM python:3.9-slim
WORKDIR /app

# Robust install without upgrading pip (to avoid potential breakage)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Use the LOCAL proto file
COPY poker.proto .
RUN python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. poker.proto

# Copy the rest of the frontend code
COPY . .

# Set explicit python buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "app.py"]
