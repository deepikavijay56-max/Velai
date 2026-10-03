import pytest
from app.core.state_machine import (
    GigStatus,
    check_valid_transition,
    validate_revision_limit,
    StateMachineError,
    VALID_GIG_TRANSITIONS,
)


def test_valid_gig_transitions():
    """All permitted transitions should not raise errors."""
    check_valid_transition(GigStatus.Draft, GigStatus.Open)
    check_valid_transition(GigStatus.Draft, GigStatus.Cancelled)
    check_valid_transition(GigStatus.Open, GigStatus.InProgress)
    check_valid_transition(GigStatus.Open, GigStatus.Cancelled)
    check_valid_transition(GigStatus.Open, GigStatus.Expired)
    check_valid_transition(GigStatus.InProgress, GigStatus.Delivered)
    check_valid_transition(GigStatus.Delivered, GigStatus.InProgress)
    check_valid_transition(GigStatus.Delivered, GigStatus.Completed)


def test_invalid_gig_transitions_rejected():
    """Forbidden transitions must strictly raise StateMachineError (HTTP 400)."""
    # Cannot jump from Open directly to Completed
    with pytest.raises(StateMachineError) as exc:
        check_valid_transition(GigStatus.Open, GigStatus.Completed)
    assert "Invalid gig state transition" in str(exc.value.detail)

    # Cannot jump from Draft directly to Delivered
    with pytest.raises(StateMachineError):
        check_valid_transition(GigStatus.Draft, GigStatus.Delivered)

    # InProgress cannot be cancelled directly without dispute
    with pytest.raises(StateMachineError):
        check_valid_transition(GigStatus.InProgress, GigStatus.Cancelled)

    # Terminal state 'Completed' cannot transition anywhere
    with pytest.raises(StateMachineError):
        check_valid_transition(GigStatus.Completed, GigStatus.Open)

    # Terminal state 'Cancelled' cannot be reopened
    with pytest.raises(StateMachineError):
        check_valid_transition(GigStatus.Cancelled, GigStatus.Open)


def test_revision_limit_validation():
    """Revisions under the limit are allowed; reaching or exceeding is rejected."""
    # Under limit: allowed
    validate_revision_limit(agreed_revisions=2, revisions_used=0)
    validate_revision_limit(agreed_revisions=2, revisions_used=1)

    # Equal to limit: rejected
    with pytest.raises(StateMachineError) as exc:
        validate_revision_limit(agreed_revisions=2, revisions_used=2)
    assert "Revision limit reached" in str(exc.value.detail)

    # Exceeding limit: rejected
    with pytest.raises(StateMachineError):
        validate_revision_limit(agreed_revisions=1, revisions_used=2)
