# Use Python base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in container
WORKDIR /app/UniHub_backend

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Default command to run the Django app
CMD ["sh", "-c", "python manage.py migrate && python manage.py shell < create_superuser.py && python manage.py runserver 0.0.0.0:8000"]
