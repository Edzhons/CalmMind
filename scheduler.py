import threading
import time
from datetime import datetime


class ReminderScheduler:
    def __init__(self, app, check_interval=30):
        self.app = app          # reference to App instance
        self.check_interval = check_interval
        self.running = True

    def start(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        while self.running:
            now = datetime.now().replace(second=0, microsecond=0)

            for entry in self.app.entries:
                # Skip if no reminder time, archived, or done
                if not getattr(entry, "reminder_time", None):
                    continue
                if entry.archived or entry.done:
                    continue

                due = entry.reminder_time.replace(second=0, microsecond=0)

                # If the reminder time matches AND not notified yet
                if due == now and not getattr(entry, "notified", False):
                    # Show popup in main thread context
                    self.app.show_reminder_popup(entry)
                    entry.notified = True
                    self.app.storage.save_entries(self.app.entries)

            time.sleep(self.check_interval)
