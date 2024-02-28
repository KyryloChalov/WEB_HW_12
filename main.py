from fastapi import FastAPI
from src.routes import contacts, db, auth, seed

import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome! This is Homework 12"}


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
app.include_router(db.router, prefix="")
app.include_router(seed.router, prefix="")


if __name__ == "__main__":
    uvicorn.run(app)
