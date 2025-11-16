from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test API", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok", "port": 8080}

@app.get("/test")
def test():
    return {"message": "API working on port 8080"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
