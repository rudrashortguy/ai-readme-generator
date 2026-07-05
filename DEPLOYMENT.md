# Deployment

## Requirements
- Ollama with `gemma2:latest` pulled
- Python 3.12+
- Node.js 20+ (for npx esprima)

## Local Setup
```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
./run.sh
```

## Docker
```bash
docker compose up --build
```

## Deploy to Render
This project can deploy on free tiers (no GPU needed). See render.yaml.
