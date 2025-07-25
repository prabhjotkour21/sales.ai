from fastapi import FastAPI
# from src.routes.meeting import router as meeting_router
from src.routes.auth import router as auth_router
# from src.routes.suggestion import router as suggestion_router
from src.routes.chatBot import router as chatbot
# from src.routes.calendar import router as calendar_router
# from src.routes.gmail_routes import router as gmail_router
from src.routes.meeting import router as meeting_router
from fastapi.routing import APIRoute

from src.routes.llmTesting import router as llm_testing_router
from src.services.meeting_scheduler import start_meeting_scheduler
import asyncio

app = FastAPI(title="Audio Uploader with Transcription & Diarization")

app.include_router(meeting_router, prefix="/api/meeting")
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
# app.include_router(suggestion_router, prefix="/api/sg")
app.include_router(chatbot, prefix="/api/chat")
# app.include_router(calendar_router, prefix="/api/calendar", tags=["Calendar"])
# app.include_router( gmail_router, prefix="/api/gmail", tags=["Gmail"])
# app.include_router(meeting_router, prefix="/api/meet", tags=["Meetings"])


# print("Registered routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"{route.path} -> methods: {route.methods}")
app.include_router(llm_testing_router, prefix="/api/llm", tags=["LLM Testing"])

@app.on_event("startup")
async def startup_event():
    # Start the meeting scheduler in the background
    asyncio.create_task(start_meeting_scheduler())
