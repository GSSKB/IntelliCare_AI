from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat_service import ChatService
from model_service import RiskModel

app = FastAPI(title="IntelliCare AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]
)

chat_service = ChatService()
risk_model = RiskModel()

@app.post("/chat")
async def chat_endpoint(message: dict):
    response = chat_service.get_response(message["message"])
    return {"response": response}

@app.post("/predict")
async def predict_endpoint(data: dict):
    risk = risk_model.predict_risk(data["symptoms_vector"])
    return {"risk": risk}

@app.get("/")
async def root():
    return {"message": "IntelliCare AI API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)