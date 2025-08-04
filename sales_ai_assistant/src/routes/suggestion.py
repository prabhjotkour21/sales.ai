from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Query, Depends
from typing import List,Dict
from bson import ObjectId
from src.services.mongo_service import (get_final_audio, 
get_real_time_transcript, get_summary_and_suggestion, save_suggestion, get_suggestions_by_user_and_session,get_googlemeeting_by_id, update_calendar_event,get_meeting_by_id,extract_number)
from src.routes.auth import verify_token
from src.services.prediction_models_service import run_instruction
from src.services.mongo_service import get_meeting_by_id
from src.services.mongo_service import meetings_collection

from src.services.deal_service import update_deal_by_id

import json


router = APIRouter()

@router.post("/suggestions")
async def create_suggestion(
    meetingId: str = Body(...),
    userId: str = Body(...),
    transcript: str = Body(...),
    suggestion: str = Body(...),
    token_data: dict = Depends(verify_token)
):
    inserted_id = await save_suggestion(meetingId, userId, transcript, suggestion)
    return {"message": "Suggestion saved", "id": str(inserted_id)}


@router.get("/suggestions/{meetingId}/{eventId}", response_model=List[dict])
async def get_suggestions(
    meetingId: str ,
    eventId: str,
    userId:str,
    # token_data: dict = Depends(verify_token)
):
    
    # userId = token_data["user_id"]
    suggestions = await get_suggestions_by_user_and_session(userId, meetingId)
    return suggestions

@router.get("/transcript/{meetingId}/{eventId}", response_model=List[dict])
async def get_transcript(
    meetingId: str,
    eventId: str,
    userId:str,
    # token_data: dict = Depends(verify_token)
):
    # userId = token_data["user_id"]
    transcript = await get_real_time_transcript(meetingId, eventId, userId)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List



@router.get("/meeting-summary-from-transcript", response_model=dict)
async def generate_summary_from_transcript(meetingId: str, userId: str):
    # 1. Get meeting from DB
    meeting = await get_googlemeeting_by_id(meetingId)
    if not meeting or meeting.get("user_id") != userId:
        raise HTTPException(status_code=404, detail="Meeting not found")

    transcript = meeting.get("transcript", [])
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # 2. Convert transcript to plain text
    full_text = "\n".join([item["text"] for item in transcript if item.get("text")])

    # 3. Run LLM to generate summary, suggestion, risk score, next step
    summary = run_instruction("Summarize the meeting in 5 lines", full_text)
    suggestion = run_instruction("What is the business suggestion from this meeting?", full_text)
    risk_score_text = run_instruction("Give a risk score (0-100) for this deal based on the summary", f"Summary:\n{summary}")
    next_step = run_instruction("Mention the next step or action item based on the meeting discussion", full_text)
    # Extract numeric risk score
    risk_score = extract_number(risk_score_text)
    # 4. Save all results to DB
    await update_calendar_event(
        meetingId,
        {
            "summary": summary,
            "suggestion": suggestion,
            "riskScore": int(risk_score),
            "next_step": next_step,
            "updatedAt": datetime.utcnow()
        }
    )

    # 5. Update related deal if exists
    meeting_doc = await get_meeting_by_id(meetingId)
    deal_id = meeting_doc.get("dealId")
    if deal_id:
        await update_deal_by_id(str(deal_id), {
            "riskScore": int(risk_score),
            "next_step": next_step
        })

    # 6. Return response
    return {
        "meetingId": meetingId,
        "userId": userId,
        "summary": summary,
        "suggestion": suggestion,
        "riskScore": int(risk_score),
        "next_step": next_step
    }


# @router.get("/meeting-summary/{meetingId}", response_model=dict)
# async def get_meeting_summary(
#     meetingId: str,
#     userId:str
#     # token_data: dict = Depends(verify_token)
# ):
#     # userId = token_data["user_id"]
#     document = await get_summary_and_suggestion(meetingId, userId)
#     if not document:
#         raise HTTPException(status_code=404, detail="Summary not found")

#     result = await get_final_audio(meetingId)
#     #LLM Instructions
#     context = f"Meeting Summary:\n{document['summary']}\nTranscript:\n{result['results']}"
#     risk_score = run_instruction("Give a risk score (0-100) for this deal based on the summary", context)
#     next_step = run_instruction("Mention the next step or action item based on the meeting discussion", context)


#     # Update related deal
#     meeting = await get_meeting_by_id(meetingId)
#     deal_id = meeting.get("dealId")

#     if deal_id:
#         await update_deal_by_id(str(deal_id), {
#             "riskScore": int(risk_score),
#             "next_step": next_step
#         })


#     return {
#         "meetingId": document["meetingId"],
#         "userId": document["userId"],
#         "summary": document["summary"],
#         "suggestion": document["suggestion"],
#         "createdAt": document["createdAt"],
#         "updatedAt": document["updatedAt"],
#         "transcript": result["results"],
#         "riskScore": int(risk_score),
#         "next_step": next_step,
#         "recording": result.get("recording_url")
#     }





# Route to get conversation insights from a specific meeting
@router.get("/conversation-insights/{meetingId}", response_model=dict)
async def get_conversation_insights(meetingId: str, token_data: dict = Depends(verify_token)):
    # Extract user ID from the token
    user_id = token_data["user_id"]

    # Fetch the document containing summary, suggestion, and transcript
    document = await get_summary_and_suggestion(meetingId, user_id)

    # If document or transcript is missing, raise an error
    if not document or "transcript" not in document:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # Extract transcript data from the document
    transcript = document["transcript"]

    # Dictionary to track total speaking time of each speaker
    speaker_time = {}

    # Variable to store total duration of the meeting
    total_time = 0

    # Loop through each transcript entry to calculate speaking duration
    for entry in transcript:
        speaker = entry["speaker"]
        duration = entry["end_time"] - entry["start_time"]
        total_time += duration  # Add to total meeting time
        speaker_time[speaker] = speaker_time.get(speaker, 0) + duration  # Accumulate speaker time

    # Prepare the response list with speaker stats
    speaker_stats = []
    for speaker, time_spoken in speaker_time.items():
        # Calculate speaking time percentage
        percentage = round((time_spoken / total_time) * 100, 2)
        speaker_stats.append({
            "speaker": speaker,
            "speakingTime": time_spoken,
            "percentage": percentage
        })

    # Final response with meeting ID, total time, and speaker-wise stats
    return {
        "meetingId": meetingId,
        "totalDuration": total_time,
        "speakerStats": speaker_stats
    }




# Route to get conversation insights for the whole team (organization)
@router.get("/conversation-insights/{organizationId}", response_model=dict)
async def get_team_conversation_insights(organizationId: str, token_data: dict = Depends(verify_token)):
    try:
        # Fetch all meetings of this organization
        meetings = await meetings_collection.find({
            "organizationId": ObjectId(organizationId),
            "isDeleted": False
        }).to_list(length=None)

        # Dictionary to track each user's total speaking time and number of conversations
        team_stats = {}  # {userId: {"name": ..., "conversations": x, "hours": y}}

        for meeting in meetings:
            user_id = meeting.get("userId")
            transcript = meeting.get("transcript", [])

            total_time = 0
            for entry in transcript:
                duration = entry["end_time"] - entry["start_time"]
                total_time += duration

            if not user_id:
                continue

            if user_id not in team_stats:
                team_stats[user_id] = {
                    "name": meeting.get("userName", "Unknown"),
                    "conversations": 0,
                    "hours": 0.0
                }

            team_stats[user_id]["conversations"] += 1
            team_stats[user_id]["hours"] += total_time / 60.0  # Convert seconds to minutes

        # Prepare final response with avgDuration calculation
        response = []
        for stats in team_stats.values():
            conversations = stats["conversations"]
            hours = round(stats["hours"], 2)
            avg_duration = round(hours * 60 / conversations, 2) if conversations > 0 else 0.0

            response.append({
                "name": stats["name"],
                "conversations": conversations,
                "hours": hours,
                "avgDuration": avg_duration
            })

        return {"teamInsights": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/question-answer/{meetingId}/{eventId}", response_model=List[Dict])
async def get_questions_answers_llm(
    meetingId: str,
    eventId: str,
    userId:str,
    # token_data: dict = Depends(verify_token)
):
    # userId = token_data["user_id"]
    chunks = await get_real_time_transcript(meetingId, userId, eventId)

    if not chunks:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # 1. Convert transcript chunks to speaker-tagged format
    speaker_lines = []
    for chunk in chunks:
        speaker = chunk.get("speaker", "Unknown")
        text = chunk.get("transcript", "").strip()
        if text:
            speaker_lines.append(f"{speaker}: {text}")
    
    full_conversation = "\n".join(speaker_lines)

    # 2. Prompt for LLM
    task = (
        "From the following meeting transcript, extract all question-answer pairs along with the speakers involved. "
        "Output must be a list of JSON objects, each containing question, question_speaker, answer, and answer_speaker."
    )

    try:
        output_text = run_instruction(task, full_conversation, max_tokens=600)

        # 3. Parse JSON string
        qa_pairs = json.loads(output_text)
        return qa_pairs

    except Exception as e:
        print(f"Error from LLM or JSON parse: {e}")
        raise HTTPException(status_code=500, detail="LLM processing failed")
