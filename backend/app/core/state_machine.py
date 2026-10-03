import enum
from typing import Dict, Set
from fastapi import HTTPException, status


class GigStatus(str, enum.Enum):
    Draft = "Draft"
    Open = "Open"
    InProgress = "InProgress"
    Delivered = "Delivered"
    Completed = "Completed"
    Expired = "Expired"
    Cancelled = "Cancelled"
    Disputed = "Disputed"


# Centralized map of allowed transitions
VALID_GIG_TRANSITIONS: Dict[GigStatus, Set[GigStatus]] = {
    GigStatus.Draft: {GigStatus.Open, GigStatus.Cancelled},
    GigStatus.Open: {GigStatus.InProgress, GigStatus.Expired, GigStatus.Cancelled},
    GigStatus.InProgress: {GigStatus.Delivered, GigStatus.Disputed},
    GigStatus.Delivered: {GigStatus.InProgress, GigStatus.Completed, GigStatus.Disputed},
    GigStatus.Completed: set(),  # Terminal state
    GigStatus.Expired: set(),    # Terminal state
    GigStatus.Cancelled: set(),  # Terminal state
    GigStatus.Disputed: {GigStatus.Completed, GigStatus.Cancelled},
}


class StateMachineError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def check_valid_transition(current_status: GigStatus, target_status: GigStatus) -> None:
    """
    Validates if transitioning from current_status to target_status is permitted.
    Raises StateMachineError if forbidden.
    """
    allowed_targets = VALID_GIG_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_targets:
        raise StateMachineError(
            f"Invalid gig state transition from '{current_status.value}' to '{target_status.value}'. "
            f"Allowed next states: {[s.value for s in allowed_targets]}."
        )


def validate_revision_limit(agreed_revisions: int, revisions_used: int) -> None:
    """
    Ensures that a poster cannot request more revisions than agreed in the contract.
    """
    if revisions_used >= agreed_revisions:
        raise StateMachineError(
            f"Revision limit reached ({revisions_used}/{agreed_revisions}). "
            "You cannot request further revisions without negotiating a new agreement."
        )
