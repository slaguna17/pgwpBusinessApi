# Angular Agent API

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoint

- `POST /evaluate/` con JSON:
```json
{
  "code": "function suma(a, b) { return a + b; }",
  "challenge_id": "basic-arithmetic"
}
```


uvicorn main:app --reload




docker buildx create --name lambda-builder --use
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64 -t store-agent . --load



uvicorn app.main:app --reload --host 0.0.0.0 --port 8000