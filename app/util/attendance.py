from typing import Any, Iterable, Optional


def member_id_key(member_id: Optional[str]) -> str:
    """Normalize a member ID for uniqueness checks."""
    return str(member_id or "").strip().upper()


def attendance_state_rank(state_id: Optional[int]) -> int:
    """Prefer a real mark over duplicated Not Specified rows."""
    if state_id == 1:
        return 4
    if state_id in (2, 3):
        return 3
    if state_id == 5:
        return 0
    return 1


def dedupe_attendance_records(records: Iterable[Any]) -> list[Any]:
    """Collapse duplicate attendance rows for the same member, keeping the strongest state."""
    by_id: dict[str, Any] = {}
    for record in records:
        member = getattr(record, "member", None)
        member_id = getattr(record, "member_id", None) or (
            getattr(member, "member_id", None) if member else None
        )
        key = member_id_key(member_id)
        if not key:
            continue
        existing = by_id.get(key)
        if existing is None:
            by_id[key] = record
            continue
        if attendance_state_rank(getattr(record, "attendance_state_id", None)) > attendance_state_rank(
            getattr(existing, "attendance_state_id", None)
        ):
            by_id[key] = record
    return list(by_id.values())


def serialize_attendance_record(record: Any) -> dict[str, Any]:
    """Build the API attendance payload for one record."""
    member = getattr(record, "member", None)
    state = getattr(record, "attendance_state", None)
    return {
        "member_id": getattr(member, "member_id", None) or getattr(record, "member_id", None),
        "member_name": {
            "en": getattr(member, "name_en", None) or "",
            "ar": getattr(member, "name_ar", None) or "",
        } if member else None,
        "attendance_state": {
            "attendance_state_id": state.attendance_state_id,
            "attendance_state_name": {
                "en": state.attendance_state_name_en,
                "ar": state.attendance_state_name_ar,
            } if state else None,
        } if state else None,
    }
