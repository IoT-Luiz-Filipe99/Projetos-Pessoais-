from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(data)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, port=500)
    
    
print("hola")
