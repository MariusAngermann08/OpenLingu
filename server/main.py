import fastapi

app = fastapi.FastAPI()

@app.get("/")
def get():
    return {"msg": "Hello World"}

