FROM node:22-alpine AS frontend
WORKDIR /build
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY patchpilot/ ./patchpilot/
COPY --from=frontend /build/dist ./web/dist
RUN useradd --create-home pilot && mkdir .data && chown pilot:pilot .data
USER pilot
EXPOSE 8017
CMD ["python", "-m", "uvicorn", "patchpilot.main:app", "--host", "0.0.0.0", "--port", "8017"]
