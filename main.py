from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI()

# Allow your Firebase frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the blazing-fast Groq client
# This automatically grabs the GROQ_API_KEY you saved in Render's Environment Variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define the data structure coming from your frontend
class AuctionState(BaseModel):
    playerName: str
    playerRole: str
    basePrice: float
    myBudget: float
    myTeam: str

@app.post("/get-advice")
async def get_advice(state: AuctionState):
    # The hidden prompt that generates the unique advice
    prompt = f"You are an expert IPL auction mentor for franchise {state.myTeam}. The player {state.playerName} ({state.playerRole}) is up for auction with a base price of {state.basePrice} Cr. Your team has {state.myBudget} Cr left in the purse. Give a punchy, 1-sentence advice on whether to bid or pass, and up to what maximum price. Do not use markdown."
    
    try:
        # Call the blazing fast Llama 3 model via Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return {"advice": chat_completion.choices[0].message.content.strip()}
    
    except Exception as e:
        # If anything goes wrong, print the exact error to the chat UI instead of freezing
        return {"advice": f"Backend Error: {str(e)}"}

@app.get("/")
def read_root():
    return {"status": "Groq AI Mentor Server is running! 🚀"}
