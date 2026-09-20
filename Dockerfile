# Dockerfile
#
# This is the "recipe" Docker follows to build our sealed box (image).
# Both the API and the UI use this SAME image - we just tell Docker to
# run a different command depending on which "role" a container should
# play (see docker-compose.yml).

FROM python:3.11-slim

# Set the "current folder" inside the box to /app
WORKDIR /app

# Copy over just the requirements file first (not the whole project yet).
# This is a Docker trick: if requirements.txt hasn't changed, Docker can
# reuse the already-installed packages instead of reinstalling everything
# from scratch every time you change a single line of code. Big time saver.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of our actual project code into the box.
COPY . .

# Document which network "doors" this box uses (informational only -
# actual publishing happens in docker-compose.yml).
EXPOSE 8000
EXPOSE 8501

# Default action if nobody says otherwise: start the API server.
# docker-compose.yml overrides this for the UI container.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
