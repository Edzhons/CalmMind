import json
import os
import tempfile
import sys
from models import EntryModel


class Storage:
    def __init__(self, filepath="data/entries.json"):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)

        self.filepath = os.path.join(base_path, filepath)

        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                f.write("[]")

    # ------------------------------------------------------------
    # LOAD
    # ------------------------------------------------------------
    def load_entries(self):
        """Load list of EntryModel objects from JSON file safely."""

        try:
            with open(self.filepath, "r") as f:
                raw_list = json.load(f)

            entries = []
            for item in raw_list:
                try:
                    entries.append(EntryModel.from_dict(item))
                except Exception as e:
                    print("Skipping invalid entry:", e)

            return entries

        except json.JSONDecodeError:
            print("WARNING: entries.json corrupted. Resetting file.")
            self._reset_file()
            return []

        except Exception as e:
            print("ERROR reading entries:", e)
            return []

    # ------------------------------------------------------------
    # SAVE (ATOMIC)
    # ------------------------------------------------------------
    def save_entries(self, entries):
        """Safely save entries using an atomic write (prevents corruption)."""

        data = [entry.to_dict() for entry in entries]

        # Atomic write → write to temp file, then replace original
        temp_fd, temp_path = tempfile.mkstemp()
        try:
            with os.fdopen(temp_fd, "w") as tmp:
                json.dump(data, tmp, indent=4)

            os.replace(temp_path, self.filepath)

        except Exception as e:
            print("ERROR saving entries:", e)
            try:
                os.remove(temp_path)
            except:
                pass

    # ------------------------------------------------------------
    # RESET FILE (USED IF CORRUPTED)
    # ------------------------------------------------------------
    def _reset_file(self):
        with open(self.filepath, "w") as f:
            json.dump([], f)
