from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
  return {"hello": "world"}

@app.get("/api/health")
async def health():
  return {"status": "ok"}

