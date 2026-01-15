import asyncio
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Acaisoft AI Gateway Simulator")

#PYDANTIC (WALIDACJA) 
class QueryRequest(BaseModel):
    user_id: int
    prompt: str = Field(..., min_length=5, description="Pytanie musi mieć min 5 znaków")
    max_tokens: int = Field(100, le=1000, description="Maksymalnie 1000 tokenów")

class QueryResponse(BaseModel):
    answer: str
    usage: int
    execution_time: float

#ASYNC LOGIC
async def call_fake_llm(prompt: str) -> str:
    await asyncio.sleep(2) 
    return f"To jest wygenerowana odpowiedź na: '{prompt}'"

#ENDPOINT 
@app.post("/generate", response_model=QueryResponse)
async def generate_response(request: QueryRequest):
    start_time = time.time()
    
    if "tajne" in request.prompt.lower():
        raise HTTPException(status_code=400, detail="Naruszenie polityki bezpieczeństwa!")

    # Wywołanie asynchroniczne
    result = await call_fake_llm(request.prompt)
    
    end_time = time.time()
    
    # Zwracamy obiekt zgodny z Pydantic, liczymy tokeny
    return QueryResponse(
        answer=result,
        usage=len(result.split()), 
        execution_time=end_time - start_time
    )

# Uruchomienie: uvicorn TestApp:app --reload