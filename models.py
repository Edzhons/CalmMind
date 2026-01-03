import datetime


class EntryModel:
    def __init__(
        self,
        type,
        title,
        details,
        time=None,
        done=False,
        archived=False,
        notified=False,
        reminder_time=None,
    ):
        self.type = type
        self.title = title
        self.details = details
        self.time = time
        self.done = done
        self.archived = archived
        self.notified = notified

        # Separate field for when to remind.
        # For new entries, reminder_time == time by default (for timed entries).
        self.reminder_time = reminder_time if reminder_time is not None else time

    # --------------------------
    # SERIALIZE TO DICT FOR JSON
    # --------------------------
    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "details": self.details,
            "time": self.time.isoformat() if self.time else None,
            "done": self.done,
            "archived": self.archived,
            "notified": self.notified,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
        }

    # --------------------------
    # PARSE FROM JSON TO OBJECT
    # --------------------------
    @staticmethod
    def from_dict(d):
        time_str = d.get("time")
        parsed_time = None

        if time_str:
            try:
                parsed_time = datetime.datetime.fromisoformat(time_str)
            except Exception:
                parsed_time = None  # fallback if corrupted

        reminder_str = d.get("reminder_time")
        parsed_reminder = None
        if reminder_str:
            try:
                parsed_reminder = datetime.datetime.fromisoformat(reminder_str)
            except Exception:
                parsed_reminder = None

        # If no reminder_time saved (older JSON), default to time
        if parsed_reminder is None:
            parsed_reminder = parsed_time

        return EntryModel(
            type=d.get("type", "idea"),
            title=d.get("title", ""),
            details=d.get("details", ""),
            time=parsed_time,
            done=d.get("done", False),
            archived=d.get("archived", False),
            notified=d.get("notified", False),
            reminder_time=parsed_reminder,
        )
