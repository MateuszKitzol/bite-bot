import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, SecretStr
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Correctly load the .env file from the backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the React frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    streaming=True,
    api_key=SecretStr(os.environ["OPENAI_API_KEY"])
)

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
def chat(message: ChatMessage):
    response = llm.invoke(message.message)
    return {"response": response.content}

@app.get("/")
def read_root():
    return {"Hello": "World"}
