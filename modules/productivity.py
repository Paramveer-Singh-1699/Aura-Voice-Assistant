import re
from datetime import datetime, timedelta
from database.database import add_note, get_notes, add_reminder, get_pending_reminders


def save_note(text):
    note_id = add_note(text.strip())
    return f"Saved note number {note_id}."


def read_notes():
    notes = get_notes()
    if not notes:
        return "You don't have any saved notes."
    return "Your recent notes: " + " ".join(
        f"Note {n['id']}: {n['content']}." for n in notes[:5]
    )


def parse_reminder(text):
    """
    Supported formats:
      remind me in 10 minutes to call Rahul
      remind me in 2 hours to study
    """
    match = re.search(
        r"remind me in (\d+)\s*(minute|minutes|min|hour|hours|hr|hrs)\s+to\s+(.+)",
        text, re.IGNORECASE
    )
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2).lower()
    task = match.group(3).strip()
    delta = timedelta(hours=amount) if unit.startswith(("hour", "hr")) else timedelta(minutes=amount)
    remind_at = (datetime.now() + delta).isoformat(timespec="seconds")
    reminder_id = add_reminder(task, remind_at)
    return f"Reminder {reminder_id} set for {amount} {unit}: {task}."


def list_reminders():
    rows = get_pending_reminders()
    if not rows:
        return "You have no pending reminders."
    return "Pending reminders: " + ". ".join(
        f"{r['content']} at {datetime.fromisoformat(r['remind_at']).strftime('%I:%M %p on %d %b')}"
        for r in rows
    )
