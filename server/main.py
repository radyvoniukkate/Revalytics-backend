from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import router
from auth import router as auth_router


app = FastAPI()

origins = [
    "http://localhost:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)

app.include_router(router)
app.include_router(auth_router)
