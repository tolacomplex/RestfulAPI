from fastapi import FastAPI
from pydantic import BaseModel   
from fastapi.responses import JSONResponse

from groq import Groq
import os, sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI()


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


class Chatbot(BaseModel):
  message: str
  
def get_response_message(user_message):
  message = user_message.lower()
  
  chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": message,
        }
    ],
    model="openai/gpt-oss-20b",
    stream=False,
  )

  return chat_completion.choices[0].message.content
  
@app.post("/chat/")
async def create_chate(request: Chatbot):
  reply = get_response_message(request.message)
  return JSONResponse({"reply": reply})

  