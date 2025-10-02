FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy deps
COPY pyproject.toml ./

# Install deps
RUN uv pip install --system -e .

# Copy source
COPY . .

# Copy factors from docs (mount or bake in)
# For dev, we'll mount; for prod, copy
# COPY ../docs/factors_defaults.yaml /app/docs/
# COPY ../docs/grid_intensity.yaml /app/docs/

CMD ["python", "-m", "worker.main"]