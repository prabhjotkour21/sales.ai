from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any ,Union
from datetime import datetime

class Attendee(BaseModel):
    email: str
    organizer: Optional[bool] = False
    responseStatus: Optional[str] = None
    self: Optional[bool] = False

class ConferenceSolution(BaseModel):
    iconUri: Optional[str] = None
    key: Optional[Dict[str, str]] = None
    name: Optional[str] = None

class EntryPoint(BaseModel):
    entryPointType: Optional[str] = None
    label: Optional[str] = None
    uri: Optional[str] = None

class ConferenceData(BaseModel):
    conferenceId: Optional[str] = None
    conferenceSolution: Optional[ConferenceSolution] = None
    entryPoints: Optional[List[EntryPoint]] = None

class EventDateTime(BaseModel):
    dateTime: datetime
    timeZone: Optional[str] = None

class Creator(BaseModel):
    email: str
    self: Optional[bool] = False

class Organizer(BaseModel):
    email: str
    self: Optional[bool] = False

class Reminders(BaseModel):
    useDefault: Optional[bool] = True

class CalendarEvent(BaseModel):
    id:Optional[str]=None
    eventId: Optional[str] = None
    summary: str
    meetingId: Optional[str] = None
    description: Optional[str] = None
    start: EventDateTime
    end: EventDateTime
    location: Optional[str] = None
    attendees: Union[List[Attendee],List[str] ]= []
    conferenceData: Optional[ConferenceData] = None
    created: EventDateTime
    updated:EventDateTime
    creator: Creator
    etag: Optional[str] = None
    eventType: Optional[str] = "default"
    hangoutLink: Optional[str] = None
    htmlLink: Optional[str] = None
    iCalUID: Optional[str] = None
    kind: str = "calendar#event"
    organizer: Organizer
    reminders: Optional[Reminders] = None
    sequence: Optional[int] = 0
    status: Optional[str] = "confirmed"
    user_id: Optional[str] = None
    isMeetingDetailsUploaded: Optional[bool] = False
    autoJoin: Optional[bool] = True
    mode: Optional[str] = "Online"


class CalendarEventCreate(BaseModel):
    summary: str
    description: Optional[str] = None
    start: EventDateTime
    end: EventDateTime
    location: Optional[str] = None
    attendees:Union[List[Attendee], List[str]] = []
    conferenceData: Optional[ConferenceData] = None
    reminders: Optional[Reminders] = None

class CalendarEventResponse(CalendarEvent):
    pass 