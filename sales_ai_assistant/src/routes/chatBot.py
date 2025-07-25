from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.prediction_models_service import run_instruction
from typing import Optional, List,Dict
router = APIRouter()

class ChatBotRequest(BaseModel):
    message: str
    description: Optional[str] = None
    product_details: Optional[str] = None

class ChatBotResponse(BaseModel):
    results: dict  # Return all meeting sections

class RevenueRequest(BaseModel):
    data: str
    requested_sections: Optional[List[str]] = None

class RevenueResponse(BaseModel):
    results: Dict[str, str]



  


# Updated dynamic version with customizable input and sections
@router.post("/chat-bot", response_model=ChatBotResponse)
async def chat_bot(request: ChatBotRequest):
    try:
        # Example formatted transcript - replace with actual if needed
        formatted_transcript = request.message

        description = request.description or "No description provided."
        product_details = request.product_details or "No product details available."

        base_context = f"Meeting Description: {description}\nProduct Details: {product_details}\nTranscript:\n{formatted_transcript}"
        # All available instruction templates
        all_instructions = {
            "Meeting Details": "Extract the meeting date (if available), time, participants, organizer, and duration.",
            "Agenda": "List the agenda items discussed or implied during the meeting.",
            "Key Discussion Points": "List the key discussion points from the meeting.",
            "Action Items / To-Dos": "List all action items with responsible persons and due dates (if mentioned).",
            "Decisions & Agreements": "List important decisions and agreements made during the meeting.",
            "Follow-up Items": "List follow-up questions or tasks that need to be addressed in the next meeting.",
            "Meeting Summary": "Summarize the entire meeting in 2-3 sentences.",
            "Sentiment / Feedback": "Analyze the tone and sentiment of each speaker and the overall meeting."
        }
        # Filter instructions based on user input
        if request.requested_sections:
            instructions = {
                key: value for key, value in all_instructions.items()
                if key in request.requested_sections
            }
        else:
            instructions = all_instructions  # Default: all sections

        results = {}
        for section, instruction in instructions.items():
            results[section] = run_instruction(instruction, base_context)

        return ChatBotResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  Revenue Summary Endpoint
@router.post("/revenue-summary", response_model=RevenueResponse)
async def revenue_summary(request: RevenueRequest):
    try:
        base_context = f"Revenue Data:\n{request.data}"

        # All available instructions
        all_instructions = {
            "Total Revenue": "Calculate the total revenue of all deals.",
            "High Risk Deals": "List the deals with Risk Score greater than 60.",
            "Next Steps": "List any upcoming steps or follow-ups required.",
            "Closed Deals Summary": "Summarize closed won and closed lost deals.",
        }

        # Filter if specific sections requested
        if request.requested_sections:
            instructions = {
                k: v for k, v in all_instructions.items()
                if k in request.requested_sections
            }
        else:
            instructions = all_instructions

        # Generate LLM output for each section
        results = {}
        for key, inst in instructions.items():
            results[key] = run_instruction(inst, base_context)

        return RevenueResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    







# @router.post("/join")
# async def join_meeting(
#     data: JoinMeetingRequest,
#     token_data: dict = Depends(verify_admin)
# ):
#     """
#     Join an external Google Meet session.
#     Only administrators can perform this action.
    
#     Args:
#         data (JoinMeetingRequest): Meeting join request data
#         token_data (dict): Token data from authentication
        
#     Returns:
#         dict: Meeting join response
        
#     Raises:
#         HTTPException: If meeting join fails
#     """
#     try:
#         # Verify user exists
#         user = await get_user_details({"email": token_data["email"]})
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )

#         # If meetingId is provided, verify it exists
#         if data.meetingId:
#             meeting = await get_meeting_by_id(data.meetingId)
#             if not meeting:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail="Meeting not found"
#                 )

#         result = await join_external_meeting(
#             gmeet_link=str(data.gmeet_link),
#             gmail_user_email=ADMIN_GMAIL_EMAIL,
#             gmail_user_password=ADMIN_GMAIL_PASSWORD,
#             duration_in_minutes=data.duration_in_minutes,
#             userId=data.userId or token_data["user_id"],
#             meetingId=data.meetingId,
#             max_wait_time_in_minutes=data.max_wait_time_in_minutes
#         )
#         return result
#     except ValueError as ve:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(ve)
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to join meeting: {str(e)}"
#         )
    



# @router.post("/chat-bot", response_model=ChatBotResponse)
# async def chat_bot(request: ChatBotRequest):
#     try:
#         # Example formatted transcript - replace with actual if needed
#         formatted_transcript = request.message

#         description = "This is a product team sync regarding the upcoming client pitch and product development progress."
#         product_details = "Product: AI-based Smart Inventory System."

#         base_context = f"Meeting Description: {description}\nProduct Details: {product_details}\nTranscript:\n{formatted_transcript}"

#         instructions = {
#             "Meeting Details": "Extract the meeting date (if available), time, participants, organizer, and duration.",
#             "Agenda": "List the agenda items discussed or implied during the meeting.",
#             "Key Discussion Points": "List the key discussion points from the meeting.",
#             "Action Items / To-Dos": "List all action items with responsible persons and due dates (if mentioned).",
#             "Decisions & Agreements": "List important decisions and agreements made during the meeting.",
#             "Follow-up Items": "List follow-up questions or tasks that need to be addressed in the next meeting.",
#             "Meeting Summary": "Summarize the entire meeting in 2-3 sentences.",
#             "Sentiment / Feedback": "Analyze the tone and sentiment of each speaker and the overall meeting."
#         }

#         results = {}
#         for section, instruction in instructions.items():
#             results[section] = run_instruction(instruction, base_context)

#         return ChatBotResponse(results=results)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

