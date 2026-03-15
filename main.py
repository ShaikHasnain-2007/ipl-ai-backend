from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Allow your Firebase frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the AI API Key (Render will inject this securely later)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

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
        response = model.generate_content(prompt)
        return {"advice": response.text.strip()}
    except Exception as e:
        # This will now print the actual error to your screen instead of getting stuck
        return {"advice": f"Backend Error: {str(e)}"}

@app.get("/")
def read_root():
    return {"status": "AI Mentor Server is running!"}
