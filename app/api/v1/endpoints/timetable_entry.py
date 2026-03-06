from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.services import timetable_entry_service
from app.schemas import timetable_entry
from app.models.user import User


router = APIRouter()

