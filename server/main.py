from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/")
def get():
    return {"msg": "Hello World"}
