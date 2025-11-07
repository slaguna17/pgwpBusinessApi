# Angular Agent API

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoint

- `POST /invoke/` con JSON:
```json
{
  "input": "Hola",
  "chat_history": [
  ]
}
```

## Deploy with docker for AWS lambda

```bash
docker buildx create --name lambda-builder --use
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64 -t store-agent . --load
```