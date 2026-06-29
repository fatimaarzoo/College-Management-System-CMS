from fastapi import FastAPI,Request
import time

app = FastAPI()

@app.middleware("http")
async def log_request_time(request:Request,call_next):
    start_time =time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.method} {request.url} - Process time: {process_time:.4f} seconds")
    return response

@app.get("/")
def read_root():
    return {"Hello" : "World"}

