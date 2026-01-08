import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import webbrowser
from models import EntryModel
from storage import Storage
from scheduler import ReminderScheduler


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("CalmMind (MVP)")

        self.feedback_url = "https://forms.gle/91opNmBzj6jmLPsJ9"

        # --- COLORS / THEME ---
        self.colors = {
            "bg": "#101018",
            "sidebar_bg": "#181824",
            "sidebar_button_bg": "#232337",
            "sidebar_button_active": "#2f2f45",
            "sidebar_button_fg": "#f5f5f7",
            "main_bg": "#141421",
            "card_bg": "#1f1f2b",
            "text_main": "#f5f5f7",
            "text_muted": "#a0a0b8",
            "idea": "#ffcc66",
            "task": "#66ccff",
            "appointment": "#ff6666",
            "accent": "#5b8def",
        }

        self.type_colors = {
            "idea": self.colors["idea"],
            "task": self.colors["task"],
            "appointment": self.colors["appointment"],
        }

        self.root.configure(bg=self.colors["bg"])

        # DATA
        self.storage = Storage("entries.json")
        self.entries = self.storage.load_entries()

        # SCHEDULER
        self.scheduler = ReminderScheduler(self)
        self.scheduler.start()

        # ACTIVE VIEW
        self.current_view = "all"  # all | next | ideas | archive

        # BUILD UI
        self.build_ui()
        
        self.bind_shortcuts()

    # ---------------- Small helper for hover ----------------
    def add_hover(self, widget, normal_bg, hover_bg):
        def on_enter(e):
            widget.configure(bg=hover_bg)
        def on_leave(e):
            widget.configure(bg=normal_bg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # ---------------- Scrollable area helper ----------------
    def create_scrollable_area(self, parent):
        canvas = tk.Canvas(
            parent,
            bg=self.colors["main_bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=canvas.yview
        )

        scrollable_frame = tk.Frame(
            canvas,
            bg=self.colors["main_bg"]
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scrollable_frame.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            )
        )

        return scrollable_frame

    # ---------------- UI BUILD ----------------
    def build_ui(self):
        # Sidebar
        sidebar = tk.Frame(
            self.root, padx=10, pady=10, bg=self.colors["sidebar_bg"]
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        def make_btn(text, view_name):
            btn = tk.Button(
                sidebar,
                text=text,
                command=lambda v=view_name: self.switch_view(v),
                bg=self.colors["sidebar_button_bg"],
                fg=self.colors["sidebar_button_fg"],
                activebackground=self.colors["sidebar_button_active"],
                activeforeground=self.colors["sidebar_button_fg"],
                bd=0,
                relief="flat",
                padx=8,
                pady=6,
                anchor="w"
            )
            self.add_hover(btn, self.colors["sidebar_button_bg"], self.colors["sidebar_button_active"])
            return btn

        make_btn("📋 All", "all").pack(fill="x", pady=2)

        new_btn = tk.Button(
            sidebar,
            text="➕ New",
            command=self.open_new,
            bg=self.colors["sidebar_button_bg"],
            fg=self.colors["sidebar_button_fg"],
            activebackground=self.colors["sidebar_button_active"],
            activeforeground=self.colors["sidebar_button_fg"],
            bd=0,
            relief="flat",
            padx=8,
            pady=6,
            anchor="w"
        )
        self.add_hover(new_btn, self.colors["sidebar_button_bg"], self.colors["sidebar_button_active"])
        new_btn.pack(fill="x", pady=2)

        make_btn("📌 Next", "next").pack(fill="x", pady=2)
        make_btn("💡 Ideas", "ideas").pack(fill="x", pady=2)
        make_btn("🗄 Archive", "archive").pack(fill="x", pady=2)

        # Spacer to push feedback button to bottom
        tk.Frame(sidebar, bg=self.colors["sidebar_bg"]).pack(expand=True, fill="both")

        feedback_btn = tk.Button(
            sidebar,
            text="💬 Feedback",
            command=self.open_feedback,
            bg=self.colors["sidebar_button_bg"],
            fg=self.colors["accent"],           # Accent color text
            activebackground=self.colors["sidebar_button_active"],
            activeforeground=self.colors["accent"],
            bd=0,
            relief="flat",
            padx=8,
            pady=6,
            anchor="w"
        )

        self.add_hover(
            feedback_btn,
            self.colors["sidebar_button_bg"],
            self.colors["sidebar_button_active"]
        )

        feedback_btn.pack(fill="x", pady=(10, 0))

        # Main panel
        self.main_panel = tk.Frame(
            self.root, padx=10, pady=10, bg=self.colors["main_bg"]
        )
        self.main_panel.pack(side=tk.RIGHT, expand=True, fill="both")

        self.refresh_current_view()

    # ---------------- Keyboard shortcuts ----------------
    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.open_new())
        self.root.bind("<Control-N>", lambda e: self.open_new())

        self.root.bind("<Control-a>", lambda e: self.switch_view("all"))
        self.root.bind("<Control-A>", lambda e: self.switch_view("all"))

        self.root.bind("<Control-t>", lambda e: self.switch_view("next"))
        self.root.bind("<Control-T>", lambda e: self.switch_view("next"))
        
        self.root.bind("<Control-i>", lambda e: self.switch_view("ideas"))
        self.root.bind("<Control-I>", lambda e: self.switch_view("ideas"))

        self.root.bind("<Control-r>", lambda e: self.switch_view("archive"))
        self.root.bind("<Control-R>", lambda e: self.switch_view("archive"))

    def bind_escape_to_close(self, window):
        window.bind("<Escape>", lambda e: window.destroy())

    # ---------------- CENTRAL VIEW SWITCH ----------------
    def switch_view(self, view_name):
        self.current_view = view_name
        self.refresh_current_view()

    def refresh_current_view(self):
        self.auto_archive_overdue()

        # FILTER BASED ON ACTIVE VIEW
        if self.current_view == "all":
            entries = [e for e in self.entries if not e.archived]

        elif self.current_view == "next":
            now = datetime.now()
            entries = [
                e for e in self.entries if e.time and e.time >= now and not e.archived
            ]
            entries.sort(key=lambda e: e.time)

        elif self.current_view == "ideas":
            entries = [
                e for e in self.entries if e.type == "idea" and not e.archived
            ]

        elif self.current_view == "archive":
            entries = [e for e in self.entries if e.archived]

        else:
            entries = [e for e in self.entries if not e.archived]

        # RENDER
        self.refresh_main_panel(entries)

    def focus_window(self, window):
        window.transient(self.root)
        window.grab_set()
        window.focus_force()

    # ---------------- MAIN VIEW RENDERING ----------------
    def refresh_main_panel(self, entries):
        for widget in self.main_panel.winfo_children():
            widget.destroy()

        if not entries:
            tk.Label(
                self.main_panel,
                text="Nothing here yet.",
                bg=self.colors["main_bg"],
                fg=self.colors["text_muted"],
                font=("Helvetica", 12, "italic")
            ).pack(anchor="center", pady=20)
            return

        # ⬇️ CREATE SCROLLABLE CONTENT AREA
        content = self.create_scrollable_area(self.main_panel)

        for entry in entries:
            card = tk.Frame(
                content,
                bg=self.colors["card_bg"],
                padx=10,
                pady=8
            )
            card.pack(fill="x", pady=6)

            # Header
            header = tk.Frame(card, bg=self.colors["card_bg"])
            header.pack(fill="x")

            # Type badge
            type_color = self.type_colors.get(entry.type, self.colors["accent"])
            tk.Label(
                header,
                text=entry.type.capitalize(),
                bg=type_color,
                fg="#000000",
                font=("Helvetica", 9, "bold"),
                padx=6,
                pady=1
            ).pack(side="left")

            # Title
            tk.Label(
                header,
                text=entry.title,
                bg=self.colors["card_bg"],
                fg=self.colors["text_main"],
                font=("Helvetica", 14, "bold"),
                padx=8
            ).pack(side="left")

            # Time
            if entry.time:
                ts = entry.time.strftime("%Y-%m-%d %H:%M")
                tk.Label(
                    header,
                    text=ts,
                    bg=self.colors["card_bg"],
                    fg=self.colors["text_muted"],
                    font=("Helvetica", 10, "italic")
                ).pack(side="right")

            # Details
            if entry.details:
                tk.Label(
                    card,
                    text=entry.details,
                    bg=self.colors["card_bg"],
                    fg=self.colors["text_main"],
                    wraplength=600,
                    justify="left"
                ).pack(anchor="w", pady=(4, 2))

            # Actions
            actions = tk.Frame(card, bg=self.colors["card_bg"])
            actions.pack(fill="x", pady=(4, 0))

            if self.current_view == "archive":
                can_restore = True

                # If it has a time AND it's more than 24h overdue → hide restore
                if entry.time:
                    age_seconds = (datetime.now() - entry.time).total_seconds()
                    if age_seconds > 24 * 3600:
                        can_restore = False

                if can_restore:
                    restore_btn = tk.Button(
                        actions,
                        text="Restore",
                        command=lambda e=entry: self.unarchive_entry(e),
                        bg="#4caf50",
                        fg="#ffffff",
                        bd=0,
                        padx=6,
                        pady=2
                    )
                    self.add_hover(restore_btn, "#4caf50", "#66bb6a")
                    restore_btn.pack(side="right", padx=4)

                delete_btn = tk.Button(
                    actions,
                    text="Delete",
                    command=lambda e=entry: self.delete_entry(e),
                    bg="#ff4d4d",
                    fg="#ffffff",
                    bd=0,
                    padx=6,
                    pady=2
                )
                self.add_hover(delete_btn, "#ff4d4d", "#ff6666")
                delete_btn.pack(side="right", padx=4)

            else:
                edit_btn = tk.Button(
                    actions,
                    text="Edit",
                    command=lambda e=entry: self.open_edit(e),
                    bg="#5b8def",
                    fg="white",
                    bd=0,
                    padx=6,
                    pady=2
                )
                self.add_hover(edit_btn, "#5b8def", "#769dff")
                edit_btn.pack(side="right", padx=4)

                archive_btn = tk.Button(
                    actions,
                    text="Archive",
                    command=lambda e=entry: self.archive_entry(e),
                    bg="#44445a",
                    fg=self.colors["text_main"],
                    bd=0,
                    padx=6,
                    pady=2
                )
                self.add_hover(archive_btn, "#44445a", "#55556b")
                archive_btn.pack(side="right", padx=4)

    # ---------------- ENTRY CREATION ----------------
    def open_new(self):
        new_window = tk.Toplevel(self.root)
        self.focus_window(new_window)
        self.bind_escape_to_close(new_window)
        new_window.title("New Entry")
        new_window.configure(bg=self.colors["main_bg"])
        new_window.geometry("500x620")
        

        # ---------- REUSABLE STYLES ----------
        LABEL_STYLE = {
            "bg": self.colors["main_bg"],
            "fg": self.colors["text_main"],
            "font": ("Helvetica", 12, "bold"),
            "anchor": "w",
            "padx": 10,
            "pady": 4
        }

        ENTRY_STYLE = {
            "bg": self.colors["card_bg"],
            "fg": self.colors["text_main"],
            "insertbackground": self.colors["accent"],
            "relief": "flat",
        }

        # Outer container
        container = tk.Frame(new_window, bg=self.colors["main_bg"])
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # TYPE SELECTOR
        tk.Label(container, text="Select type:", **LABEL_STYLE).pack(fill="x")

        selected_type = tk.StringVar(value="idea")
        type_frame = tk.Frame(container, bg=self.colors["main_bg"])
        type_frame.pack(fill="x", pady=(0, 10))

        def make_radio(text, value):
            return tk.Radiobutton(
                type_frame,
                text=text,
                variable=selected_type,
                value=value,
                bg=self.colors["main_bg"],
                fg=self.colors["text_main"],
                selectcolor=self.colors["sidebar_bg"],
                activebackground=self.colors["main_bg"],
                activeforeground=self.colors["text_main"],
                highlightthickness=0,
                font=("Helvetica", 11)
            )

        make_radio("Idea", "idea").pack(side="left", padx=10)
        make_radio("Task", "task").pack(side="left", padx=10)
        make_radio("Appointment", "appointment").pack(side="left", padx=10)

        task_time_var = tk.BooleanVar(value=False)

        # Checkbox for task time
        task_time_checkbox = tk.Checkbutton(
            container,
            text="Set a time",
            variable=task_time_var,
            bg=self.colors["main_bg"],
            fg=self.colors["text_muted"],
            activebackground=self.colors["main_bg"],
            selectcolor=self.colors["sidebar_bg"],
            font=("Helvetica", 10)
        )

        # TITLE
        tk.Label(container, text="Title:", **LABEL_STYLE).pack(fill="x")
        title_entry = tk.Entry(container, width=40, **ENTRY_STYLE)
        title_entry.pack(fill="x", padx=10, pady=(0, 10))
        title_entry.focus_set()

        # DETAILS
        tk.Label(container, text="Details:", **LABEL_STYLE).pack(fill="x")
        content_text = tk.Text(container, height=8, wrap="word", **ENTRY_STYLE)
        content_text.pack(fill="both", padx=10, pady=(0, 10))

        # DATE/TIME CONTAINER
        tk.Label(container, text="Date & Time:", **LABEL_STYLE).pack(fill="x")

        time_card = tk.Frame(container, bg=self.colors["card_bg"])
        time_card.pack(fill="x", padx=10, pady=5)

        date_label = tk.Label(time_card, text="Date:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        date_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        date_picker = DateEntry(
            time_card,
            width=12,
            background=self.colors["accent"],
            foreground="white",
            borderwidth=0,
            date_pattern="yyyy-mm-dd",
            justify="center",
            selectbackground=self.colors["accent"],
            selectforeground="white",
            normalbackground=self.colors["card_bg"],
            normalforeground=self.colors["text_main"],
        )
        date_picker.grid(row=0, column=1, padx=5, pady=5)

        hour_label = tk.Label(time_card, text="Hour:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        hour_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        hour_box = ttk.Combobox(time_card, values=[f"{i:02d}" for i in range(24)], width=4, state="readonly")
        hour_box.set("12")
        hour_box.grid(row=1, column=1, padx=5, pady=5)

        minute_label = tk.Label(time_card, text="Minute:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        minute_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        minute_box = ttk.Combobox(time_card, values=[f"{i:02d}" for i in range(60)], width=4, state="readonly")
        minute_box.set("00")
        minute_box.grid(row=2, column=1, padx=5, pady=5)

        # TIME UI LOGIC
        def update_time_ui(*args):
            def disable(dp):
                try:
                    dp.entry_widget.config(state="disabled")
                except Exception:
                    dp.configure(state="disabled")

            def enable(dp):
                try:
                    dp.entry_widget.config(state="normal")
                except Exception:
                    dp.configure(state="normal")

            t = selected_type.get()
            task_time_checkbox.pack_forget()

            if t == "idea":
                disable(date_picker)
                hour_box.config(state="disabled")
                minute_box.config(state="disabled")

            elif t == "task":
                task_time_checkbox.pack(anchor="w", padx=10)
                if task_time_var.get():
                    enable(date_picker)
                    hour_box.config(state="readonly")
                    minute_box.config(state="readonly")
                else:
                    disable(date_picker)
                    hour_box.config(state="disabled")
                    minute_box.config(state="disabled")

            elif t == "appointment":
                enable(date_picker)
                hour_box.config(state="readonly")
                minute_box.config(state="readonly")

        selected_type.trace_add("write", update_time_ui)
        task_time_var.trace_add("write", lambda *_: update_time_ui())
        update_time_ui()

        # SAVE BUTTON
        save_btn = tk.Button(
            container,
            text="Save Entry",
            bg=self.colors["accent"],
            fg="#ffffff",
            bd=0,
            relief="flat",
            padx=10,
            pady=8,
            font=("Helvetica", 12, "bold")
        )
        self.add_hover(save_btn, self.colors["accent"], "#769dff")
        save_btn.pack(fill="x", padx=10, pady=15)

        # SAVE LOGIC
        def save():
            entry_type = selected_type.get()
            title = title_entry.get().strip()
            details = content_text.get("1.0", tk.END).strip()
            parsed_time = None

            if not title:
                messagebox.showerror("Error", "Title cannot be empty.")
                return

            if entry_type == "task" and task_time_var.get():
                parsed_time = datetime(
                    date_picker.get_date().year,
                    date_picker.get_date().month,
                    date_picker.get_date().day,
                    int(hour_box.get()),
                    int(minute_box.get())
                )

            elif entry_type == "appointment":
                parsed_time = datetime(
                    date_picker.get_date().year,
                    date_picker.get_date().month,
                    date_picker.get_date().day,
                    int(hour_box.get()),
                    int(minute_box.get())
                )

            new_entry = EntryModel(
                type=entry_type,
                title=title,
                details=details,
                time=parsed_time,
                done=False,
                archived=False,
                notified=False,
                reminder_time=parsed_time
            )

            self.entries.append(new_entry)
            self.storage.save_entries(self.entries)
            self.refresh_current_view()
            new_window.destroy()

        save_btn.configure(command=save)

    # ---------------- ENTRY EDITING ----------------
    def open_edit(self, entry):
        edit_win = tk.Toplevel(self.root)
        self.focus_window(edit_win)
        edit_win.title("Edit Entry")
        edit_win.configure(bg=self.colors["main_bg"])
        edit_win.geometry("500x620")

        # ---------- STYLES ----------
        LABEL_STYLE = {
            "bg": self.colors["main_bg"],
            "fg": self.colors["text_main"],
            "font": ("Helvetica", 12, "bold"),
            "anchor": "w",
            "padx": 10,
            "pady": 4
        }

        ENTRY_STYLE = {
            "bg": self.colors["card_bg"],
            "fg": self.colors["text_main"],
            "insertbackground": self.colors["accent"],
            "relief": "flat",
        }

        container = tk.Frame(edit_win, bg=self.colors["main_bg"])
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # TYPE SELECT
        tk.Label(container, text="Type:", **LABEL_STYLE).pack(fill="x")
        selected_type = tk.StringVar(value=entry.type)

        type_frame = tk.Frame(container, bg=self.colors["main_bg"])
        type_frame.pack(fill="x", pady=(0, 10))

        def make_radio(text, val):
            return tk.Radiobutton(
                type_frame,
                text=text,
                variable=selected_type,
                value=val,
                bg=self.colors["main_bg"],
                fg=self.colors["text_main"],
                selectcolor=self.colors["sidebar_bg"],
                activebackground=self.colors["main_bg"],
                activeforeground=self.colors["text_main"],
                highlightthickness=0,
                font=("Helvetica", 11)
            )

        make_radio("Idea", "idea").pack(side="left", padx=10)
        make_radio("Task", "task").pack(side="left", padx=10)
        make_radio("Appointment", "appointment").pack(side="left", padx=10)

        # TASK time toggle
        task_time_var = tk.BooleanVar(value=entry.type=="task" and entry.time is not None)

        task_time_checkbox = tk.Checkbutton(
            container,
            text="Set a time",
            variable=task_time_var,
            bg=self.colors["main_bg"],
            fg=self.colors["text_muted"],
            activebackground=self.colors["main_bg"],
            selectcolor=self.colors["sidebar_bg"],
            font=("Helvetica", 10)
        )

        # TITLE
        tk.Label(container, text="Title:", **LABEL_STYLE).pack(fill="x")
        title_entry = tk.Entry(container, width=40, **ENTRY_STYLE)
        title_entry.insert(0, entry.title)
        title_entry.pack(fill="x", padx=10, pady=(0, 10))
        title_entry.focus_set()

        # DETAILS
        tk.Label(container, text="Details:", **LABEL_STYLE).pack(fill="x")
        content_text = tk.Text(container, height=8, wrap="word", **ENTRY_STYLE)
        content_text.insert("1.0", entry.details)
        content_text.pack(fill="both", padx=10, pady=(0, 10))

        # DATE/TIME CARD
        tk.Label(container, text="Date & Time:", **LABEL_STYLE).pack(fill="x")

        time_card = tk.Frame(container, bg=self.colors["card_bg"])
        time_card.pack(fill="x", padx=10, pady=5)

        date_label = tk.Label(time_card, text="Date:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        date_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        date_picker = DateEntry(
            time_card,
            width=12,
            background=self.colors["accent"],
            foreground="white",
            borderwidth=0,
            date_pattern="yyyy-mm-dd",
            justify="center"
        )
        date_picker.grid(row=0, column=1, padx=5, pady=5)

        hour_label = tk.Label(time_card, text="Hour:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        hour_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        hour_box = ttk.Combobox(time_card, values=[f"{i:02d}" for i in range(24)], width=4, state="readonly")
        hour_box.grid(row=1, column=1, padx=5, pady=5)

        minute_label = tk.Label(time_card, text="Minute:", bg=self.colors["card_bg"], fg=self.colors["text_main"])
        minute_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        minute_box = ttk.Combobox(time_card, values=[f"{i:02d}" for i in range(60)], width=4, state="readonly")
        minute_box.grid(row=2, column=1, padx=5, pady=5)

        # PREFILL TIME IF ANY
        if entry.time:
            date_picker.set_date(entry.time.date())
            hour_box.set(f"{entry.time.hour:02d}")
            minute_box.set(f"{entry.time.minute:02d}")
        else:
            hour_box.set("12")
            minute_box.set("00")

        # TIME UI LOGIC
        def refresh_time_ui(*args):
            t = selected_type.get()

            if t == "idea":
                date_picker.config(state="disabled")
                hour_box.config(state="disabled")
                minute_box.config(state="disabled")
                task_time_checkbox.pack_forget()
            elif t == "task":
                task_time_checkbox.pack(anchor="w", padx=10)
                if task_time_var.get():
                    date_picker.config(state="normal")
                    hour_box.config(state="readonly")
                    minute_box.config(state="readonly")
                else:
                    date_picker.config(state="disabled")
                    hour_box.config(state="disabled")
                    minute_box.config(state="disabled")
            else:  # appointment
                date_picker.config(state="normal")
                hour_box.config(state="readonly")
                minute_box.config(state="readonly")
                task_time_checkbox.pack_forget()

        selected_type.trace_add("write", refresh_time_ui)
        task_time_var.trace_add("write", refresh_time_ui)
        refresh_time_ui()

        # SAVE EDIT
        save_btn = tk.Button(
            container,
            text="Save Changes",
            bg=self.colors["accent"],
            fg="white",
            bd=0,
            padx=10,
            pady=8,
            font=("Helvetica", 12, "bold")
        )
        self.add_hover(save_btn, self.colors["accent"], "#769dff")
        save_btn.pack(fill="x", padx=10, pady=15)

        def save_changes():
            entry.type = selected_type.get()
            entry.title = title_entry.get().strip()
            entry.details = content_text.get("1.0", tk.END).strip()

            if entry.type == "appointment":
                entry.time = datetime(
                    date_picker.get_date().year,
                    date_picker.get_date().month,
                    date_picker.get_date().day,
                    int(hour_box.get()),
                    int(minute_box.get())
                )
            elif entry.type == "task":
                if task_time_var.get():
                    entry.time = datetime(
                        date_picker.get_date().year,
                        date_picker.get_date().month,
                        date_picker.get_date().day,
                        int(hour_box.get()),
                        int(minute_box.get())
                    )
                else:
                    entry.time = None
            else:  # idea
                entry.time = None

            # Reset reminder to point to the updated time
            entry.notified = False
            entry.reminder_time = entry.time

            self.storage.save_entries(self.entries)
            self.refresh_current_view()
            edit_win.destroy()

        save_btn.configure(command=save_changes)

    # ---------------- ACTIONS ----------------
    def archive_entry(self, entry):
        entry.archived = True
        self.storage.save_entries(self.entries)
        self.refresh_current_view()

    def unarchive_entry(self, entry):
        entry.archived = False
        self.storage.save_entries(self.entries)
        self.refresh_current_view()

    def delete_entry(self, entry):
        if entry in self.entries:
            self.entries.remove(entry)
            self.storage.save_entries(self.entries)
        self.refresh_current_view()

    # ---------------- AUTO ARCHIVE LOGIC ----------------
    def auto_archive_overdue(self):
        now = datetime.now()
        changed = False

        for entry in self.entries:
            if entry.time and not entry.archived:
                # Archive items > 24 hours old
                if (now - entry.time).total_seconds() > 24 * 3600:
                    entry.archived = True
                    changed = True

        if changed:
            self.storage.save_entries(self.entries)

    # ---------------- REMINDER POPUP ----------------
    def show_reminder_popup(self, entry):
        popup = tk.Toplevel(self.root)
        popup.title("Reminder")
        popup.configure(bg=self.colors["card_bg"])
        popup.geometry("380x260")
        popup.attributes("-topmost", True)

        # Type badge
        type_color = self.type_colors.get(entry.type, self.colors["accent"])
        header = tk.Frame(popup, bg=self.colors["card_bg"])
        header.pack(fill="x", pady=(10, 0))

        tk.Label(
            header,
            text=entry.type.capitalize(),
            bg=type_color,
            fg="#000000",
            font=("Helvetica", 9, "bold"),
            padx=6,
            pady=1
        ).pack(side="left", padx=10)

        tk.Label(
            header,
            text="🔔 Reminder",
            bg=self.colors["card_bg"],
            fg=self.colors["text_main"],
            font=("Helvetica", 16, "bold")
        ).pack(side="left", padx=8)

        # Time info
        if entry.time:
            ts = entry.time.strftime("%Y-%m-%d %H:%M")
            tk.Label(
                popup,
                text=f"Scheduled for: {ts}",
                bg=self.colors["card_bg"],
                fg=self.colors["text_muted"],
                font=("Helvetica", 10, "italic")
            ).pack(pady=(4, 2))

        # Title
        tk.Label(
            popup,
            text=entry.title,
            bg=self.colors["card_bg"],
            fg=self.colors["text_main"],
            font=("Helvetica", 14)
        ).pack(pady=5)

        # Details
        if entry.details:
            tk.Label(
                popup,
                text=entry.details,
                bg=self.colors["card_bg"],
                fg=self.colors["text_muted"],
                wraplength=320,
                justify="center"
            ).pack(pady=5)

        # Buttons row
        btn_row = tk.Frame(popup, bg=self.colors["card_bg"])
        btn_row.pack(pady=15)

        def snooze(minutes):
            entry.reminder_time = datetime.now() + timedelta(minutes=minutes)
            entry.notified = False
            self.storage.save_entries(self.entries)
            popup.destroy()

        def mark_done():
            entry.done = True
            entry.archived = True
            entry.notified = True
            self.storage.save_entries(self.entries)
            self.refresh_current_view()
            popup.destroy()

        snooze5 = tk.Button(
            btn_row,
            text="Snooze 5 min",
            command=lambda: snooze(5),
            bg="#44445a",
            fg=self.colors["text_main"],
            bd=0,
            padx=8,
            pady=5
        )
        self.add_hover(snooze5, "#44445a", "#55556b")
        snooze5.pack(side="left", padx=5)

        snooze10 = tk.Button(
            btn_row,
            text="Snooze 10 min",
            command=lambda: snooze(10),
            bg="#44445a",
            fg=self.colors["text_main"],
            bd=0,
            padx=8,
            pady=5
        )
        self.add_hover(snooze10, "#44445a", "#55556b")
        snooze10.pack(side="left", padx=5)

        done_btn = tk.Button(
            btn_row,
            text="Done",
            command=mark_done,
            bg="#4caf50",
            fg="#ffffff",
            bd=0,
            padx=8,
            pady=5
        )
        self.add_hover(done_btn, "#4caf50", "#66bb6a")
        done_btn.pack(side="left", padx=5)

        # Dismiss button
        tk.Button(
            popup,
            text="Close",
            command=popup.destroy,
            bg=self.colors["accent"],
            fg="white",
            bd=0,
            padx=10,
            pady=6,
            font=("Helvetica", 11, "bold")
        ).pack(pady=(0, 10))

    def open_feedback(self):
        try:
            webbrowser.open(self.feedback_url)
        except Exception:
            messagebox.showerror(
                "Error",
                "Could not open feedback form in browser."
            )

if __name__ == "__main__":
    root = tk.Tk()
    #root.geometry("650x400")
    root.minsize(650, 400)  # prevents breaking layout
    App(root)
    root.mainloop()
