from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llm import query_claude

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/query")  # Changed route to be more RESTful
async def get_response(q: str = ""):
    if not q:
        return {"message": "Please provide a query using ?q=your_question"}
    
    response = query_claude(q)
    return {"response": response}