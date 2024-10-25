# Dockerfile

# Step 1: Base image
FROM python:3.12-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the Pipfile and Pipfile.lock, and install dependencies
COPY Pipfile Pipfile.lock /app/

# Install pipenv and the dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Step 4: Copy the rest of the application code
COPY . /app

# Step 5: Expose the port that Hypercorn will use
EXPOSE 8000

# Step 6: Define the entry point command for the container
CMD ["pipenv", "run", "hypercorn", "movie_fixer.webapp:WEB_APP", "--bind", "0.0.0.0:8096"]
