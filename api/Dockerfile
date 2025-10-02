FROM python:3.12-slim

WORKDIR /app

# Install uv (fast Python package installer)
RUN pip install --no-cache-dir uv

# Copy deps
COPY pyproject.toml ./

# Install deps
RUN uv pip install --system -e .

# Copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]