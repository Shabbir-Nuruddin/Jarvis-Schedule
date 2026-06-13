"""
Jarvis Focus Guardian — Fast Blocker + Text Chat
=================================================
RUN: py -3.11 jarvis_guardian.py
"""

import os, sys, time, threading, webbrowser, ctypes
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime, time as dt_time

GEMINI_API_KEY = "AIzaSyAVu7ULPWqEkVGz866lhIfdQS_FG0qOcHc"   # paste your key here

CHECK_INTERVAL = 3
OVERRIDE_MINS  = 10

SCHEDULE = [
    (dt_time(6,0),  dt_time(6,20),  "Morning startup - mirror, no phone",        None,                             False),
    (dt_time(6,30), dt_time(7,0),   "Breakfast - eggs or oats, no sugar",         None,                             False),
    (dt_time(7,0),  dt_time(7,30),  "Learning block - Lean Startup or CS50",      "https://www.khanacademy.org",    True),
    (dt_time(7,30), dt_time(7,50),  "News brief - Gauntlet app News tab",         None,                             True),
    (dt_time(7,50), dt_time(8,45),  "Full workout - check Workout tab",           None,                             False),
    (dt_time(9,0),  dt_time(11,0),  "DEEP WORK - one task, phone away",           None,                             True),
    (dt_time(11,10),dt_time(11,30), "Social reach-out - DM one person",           "https://linkedin.com",           True),
    (dt_time(12,10),dt_time(12,35), "Quran revision - Quran.com",                 "https://quran.com",              True),
    (dt_time(12,55),dt_time(13,20), "Arabic study - Duolingo",                    "https://www.duolingo.com",       True),
    (dt_time(13,20),dt_time(14,55), "Learning block 2 - Coursera",                "https://www.coursera.org",       True),
    (dt_time(14,55),dt_time(15,20), "Punching bag - 6 rounds 2 mins each",        None,                             False),
    (dt_time(15,30),dt_time(15,55), "Spanish - Language Transfer + Duolingo",     "https://www.duolingo.com",       True),
    (dt_time(15,55),dt_time(17,25), "Income work - brand deals or product",       None,                             True),
    (dt_time(17,30),dt_time(18,0),  "Reading - Atomic Habits",                    None,                             False),
    (dt_time(18,0), dt_time(18,25), "Pull-ups and core",                          None,                             False),
    (dt_time(18,40),dt_time(19,25), "Free course - Coursera or HubSpot",          "https://www.coursera.org",       True),
    (dt_time(21,10),dt_time(22,0),  "Wind down - book reflection phone away",     None,                             False),
]

BLOCKED = [
    "youtube.com","youtube","instagram.com","instagram",
    "tiktok.com","tiktok","snapchat.com","snapchat",
    "twitter.com","x.com","facebook.com","reddit.com",
    "netflix.com","twitch.tv","9gag.com","buzzfeed",
]

ALLOWED = [
    "quran.com","coursera","khanacademy","duolingo","notion",
    "docs.google","linkedin","techcrunch","gauntlet","code",
    "python","stackoverflow","github","hubspot",
]

TASK_SEARCH = {
    "workout":      "https://www.youtube.com/results?search_query=home+dumbbell+workout",
    "punching bag": "https://www.youtube.com/results?search_query=punching+bag+workout",
    "pull-ups":     "https://www.youtube.com/results?search_query=pull+up+progression",
    "reading":      "https://www.google.com/search?q=atomic+habits+pdf+free",
    "deep work":    "https://www.google.com/search?q=deep+work+techniques",
    "social":       "https://linkedin.com",
    "income":       "https://www.google.com/search?q=brand+deals+instagram",
}

_model = None

SHABBIR_CTX = (
    "You are JARVIS. Shabbir is 18, Dubai, going to Tetr College of Business "
    "(7 countries, students build real businesses, first cohort $324K revenue). "
    "Co-founded @TheRashidaDiaries and CFO.AI. Zero income. Memorised Quran, wants Ijazah. "
    "Learning Arabic + Spanish. Responds to harsh truth. "
    "Rules: 2-3 sentences max. No bullets. Be JARVIS. Call him sir."
)

def init_gemini():
    global _model
    if not GEMINI_API_KEY:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=SHABBIR_CTX)
        return True
    except Exception as e:
        print("Gemini error:", e)
        return False

def ask_gemini(prompt):
    if not _model:
        return "API not connected. Add your key to GEMINI_API_KEY in jarvis_guardian.py."
    try:
        return _model.generate_content(prompt).text.strip()
    except Exception as e:
        return "Error: " + str(e)[:60]

def current_task():
    now = datetime.now().time()
    for start, end, desc, url, block_enabled in SCHEDULE:
        if start <= now <= end:
            return desc, url, block_enabled
    return None, None, False

def next_task():
    now = datetime.now().time()
    for start, end, desc, url, _ in SCHEDULE:
        if now < start:
            h = start.hour % 12 or 12
            p = "AM" if start.hour < 12 else "PM"
            return desc, str(h) + ":" + str(start.minute).zfill(2) + " " + p
    return None, None

def get_task_url(desc, url):
    if url:
        return url
    dl = desc.lower()
    for kw, su in TASK_SEARCH.items():
        if kw in dl:
            return su
    q = desc.split("-")[0].strip().replace(" ", "+")
    return "https://www.google.com/search?q=" + q

def get_active_window():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.lower()
    except Exception:
        return ""

def is_distraction(window):
    if not window:
        return False, ""
    if any(a in window for a in ALLOWED):
        return False, ""
    for b in BLOCKED:
        if b in window:
            return True, b
    return False, ""

def close_active_tab():
    try:
        import pyautogui
        pyautogui.hotkey("ctrl", "w")
    except Exception:
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        except Exception:
            pass

_override_until = None
_override_lock  = threading.Lock()

def set_override(minutes):
    global _override_until
    with _override_lock:
        _override_until = datetime.now().timestamp() + (minutes * 60)

def cancel_override():
    global _override_until
    with _override_lock:
        _override_until = None

def is_overridden():
    with _override_lock:
        if _override_until is None:
            return False
        return datetime.now().timestamp() < _override_until

def override_remaining():
    with _override_lock:
        if _override_until is None:
            return 0
        return max(0, int((_override_until - datetime.now().timestamp()) / 60))

_last_blocked = ""
_last_block_t = 0
_ui_log       = None

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    full = "[" + ts + "] " + msg
    if _ui_log:
        _ui_log(full)
    print(full)

def monitor_loop():
    global _last_blocked, _last_block_t
    log("Monitor started - checking every 3 seconds")
    while True:
        try:
            if is_overridden():
                time.sleep(CHECK_INTERVAL)
                continue
            task, url, block_enabled = current_task()
            if not block_enabled:
                time.sleep(CHECK_INTERVAL)
                continue
            window = get_active_window()
            distracted, matched = is_distraction(window)
            if distracted:
                now = time.time()
                close_active_tab()
                task_short = task.split("-")[0].strip() if task else "your task"
                log("Closed: " + matched + " | Task: " + task_short)
                if matched != _last_blocked or (now - _last_block_t) > 60:
                    _last_blocked = matched
                    _last_block_t = now
                    dest = get_task_url(task, url) if task else "https://google.com"
                    time.sleep(0.4)
                    webbrowser.open(dest)
                    log("Opened: " + dest[:60])
                    try:
                        from win10toast import ToastNotifier
                        ToastNotifier().show_toast(
                            "Jarvis",
                            "Back to: " + task_short,
                            duration=4, threaded=True
                        )
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(CHECK_INTERVAL)


class JarvisUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#0f0f0f")
        self._build_ui()
        self._start_status_loop()

    def _build_ui(self):
        hdr = tk.Frame(self.root, bg="#0f0f0f")
        hdr.pack(fill="x", padx=12, pady=(12, 0))
        tk.Label(hdr, text="JARVIS", font=("Consolas", 16, "bold"),
                 bg="#0f0f0f", fg="#e8c547").pack(side="left")
        self.status_lbl = tk.Label(hdr, text="", font=("Consolas", 9),
                                   bg="#0f0f0f", fg="#555")
        self.status_lbl.pack(side="right")

        self.task_lbl = tk.Label(
            self.root, text="Loading...", font=("Consolas", 9),
            bg="#0f0f0f", fg="#aaa", wraplength=380, justify="left", anchor="w"
        )
        self.task_lbl.pack(fill="x", padx=12, pady=(4, 0))

        tk.Frame(self.root, bg="#222", height=1).pack(fill="x", padx=12, pady=6)

        self.log_box = scrolledtext.ScrolledText(
            self.root, height=11, font=("Consolas", 8),
            bg="#0a0a0a", fg="#666", insertbackground="#e8c547",
            relief="flat", borderwidth=0, wrap="word", state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=12)

        tk.Frame(self.root, bg="#222", height=1).pack(fill="x", padx=12, pady=6)

        btn_f = tk.Frame(self.root, bg="#0f0f0f")
        btn_f.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(btn_f, text="Override:", font=("Consolas", 8),
                 bg="#0f0f0f", fg="#555").pack(side="left")
        for mins, lbl in [(5, "5m"), (10, "10m"), (20, "20m"), (60, "1hr")]:
            tk.Button(
                btn_f, text=lbl, font=("Consolas", 8),
                bg="#1a1a1a", fg="#e8c547", relief="flat",
                activebackground="#222", activeforeground="#e8c547",
                padx=5, pady=2, command=lambda m=mins: self._override(m)
            ).pack(side="left", padx=2)
        tk.Button(
            btn_f, text="Cancel", font=("Consolas", 8),
            bg="#1a1a1a", fg="#f06565", relief="flat",
            activebackground="#222", padx=5, pady=2,
            command=self._cancel
        ).pack(side="left", padx=2)

        inp_f = tk.Frame(self.root, bg="#0f0f0f")
        inp_f.pack(fill="x", padx=12, pady=(0, 12))
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            inp_f, textvariable=self.input_var,
            font=("Consolas", 10), bg="#1a1a1a", fg="#f0ede8",
            insertbackground="#e8c547", relief="flat", borderwidth=0
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))
        self.entry.insert(0, "Ask Jarvis or type override...")
        self.entry.bind("<FocusIn>", lambda e: self.entry.delete(0, "end")
                        if self.input_var.get() == "Ask Jarvis or type override..." else None)
        self.entry.bind("<Return>", self._send)
        tk.Button(
            inp_f, text="->", font=("Consolas", 11, "bold"),
            bg="#e8c547", fg="#000", relief="flat",
            activebackground="#c9a820", padx=8, pady=4,
            command=self._send
        ).pack(side="right")

    def add_log(self, msg):
        def _do():
            self.log_box.config(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.root.after(0, _do)

    def _override(self, minutes):
        set_override(minutes)
        self.add_log("Override: " + str(minutes) + " min granted. Browse freely.")

    def _cancel(self):
        cancel_override()
        self.add_log("Override cancelled. Blocking resumed.")

    def _send(self, event=None):
        msg = self.input_var.get().strip()
        if not msg or msg == "Ask Jarvis or type override...":
            return
        self.input_var.set("")
        self.add_log("You: " + msg)
        ml = msg.lower()

        if any(w in ml for w in ["override", "pause", "allow", "let me", "i need"]):
            mins = OVERRIDE_MINS
            for w, m in [("hour", 60), ("30", 30), ("20", 20), ("15", 15), ("10", 10), ("5", 5)]:
                if w in ml:
                    mins = m
                    break
            set_override(mins)
            self.add_log("Jarvis: Override granted for " + str(mins) + " minutes, sir.")
            return

        if any(w in ml for w in ["cancel override", "resume", "stop override"]):
            self._cancel()
            return

        if any(w in ml for w in ["what should", "current task", "what am i"]):
            t, _, _ = current_task()
            n, nt = next_task()
            if t:
                self.add_log("Jarvis: Right now - " + t)
            elif n:
                self.add_log("Jarvis: Free time. Next: " + n + " at " + str(nt))
            return

        if any(w in ml for w in ["open ", "take me", "go to", "navigate"]):
            dest = None
            if "quran" in ml:      dest = "https://quran.com"
            elif "duolingo" in ml: dest = "https://duolingo.com"
            elif "coursera" in ml: dest = "https://coursera.org"
            elif "linkedin" in ml: dest = "https://linkedin.com"
            elif "youtube" in ml and is_overridden(): dest = "https://youtube.com"
            else:
                t, u, _ = current_task()
                if t and u: dest = u
            if dest:
                webbrowser.open(dest)
                self.add_log("Jarvis: Opened " + dest)
                return

        t, _, _ = current_task()
        n, nt = next_task()
        ctx = "Time: " + datetime.now().strftime("%H:%M") + ". "
        ctx += ("Task: " + t + ".") if t else ("Free. Next: " + str(n) + " at " + str(nt) + ".")
        if is_overridden():
            ctx += " Override: " + str(override_remaining()) + "m left."

        def _ask():
            r = ask_gemini(ctx + " Shabbir: " + msg)
            self.add_log("Jarvis: " + r)
        threading.Thread(target=_ask, daemon=True).start()

    def _start_status_loop(self):
        def _upd():
            t, _, blk = current_task()
            n, nt = next_task()
            if t:
                self.task_lbl.config(text="Now: " + t, fg="#e8c547" if blk else "#aaa")
            elif n:
                self.task_lbl.config(text="Free - Next: " + str(n) + " at " + str(nt), fg="#555")
            else:
                self.task_lbl.config(text="Schedule done for today.", fg="#555")
            if is_overridden():
                self.status_lbl.config(text="Override: " + str(override_remaining()) + "m", fg="#e8c547")
            elif blk:
                self.status_lbl.config(text="Blocking", fg="#3ecf8e")
            else:
                self.status_lbl.config(text="Free", fg="#555")
            self.root.after(1000, _upd)
        _upd()

    def run(self):
        self.root.mainloop()


def main():
    if not GEMINI_API_KEY:
        print("No API key - add to GEMINI_API_KEY in this file for AI responses.")
        print("Jarvis will still block and monitor without it.")
    init_gemini()
    ui = JarvisUI()
    global _ui_log
    _ui_log = ui.add_log
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    ui.add_log("Jarvis online. Monitoring every 3 seconds.")
    ui.add_log("AI: " + ("Connected" if _model else "No key - add GEMINI_API_KEY"))
    task, _, blk = current_task()
    if task:
        ui.add_log("Current task: " + task)
    ui.run()


if __name__ == "__main__":
    main()