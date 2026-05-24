"""
Virtual Personal Assistant - UPGRADED VERSION
=============================================
All upgrades are marked with:
  # UPGRADE X: Name of upgrade
so you can find exactly what was added and where.
"""

# ──────────────────────────────────────────
# IMPORTS — TOP OF FILE
# Original imports stay, new ones added below
# ──────────────────────────────────────────
import datetime
import webbrowser
import re
import random
import json                          # UPGRADE 3: Session logging
import sqlite3                       # UPGRADE 12: Database
import requests                      # UPGRADE 7: Weather API
import smtplib                       # UPGRADE 8: Email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import Counter      # UPGRADE 3: Session stats

# Original ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# UPGRADE 6: Better ML model
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings('ignore')


# ──────────────────────────────────────────
# UPGRADE 12: DATABASE CLASS
# Put this BEFORE the main assistant class
# ──────────────────────────────────────────
class FactoryDatabase:
    """Stores defect reports, maintenance requests, production logs"""

    def __init__(self):
        self.conn = sqlite3.connect("factory_data.db")
        self._create_tables()
        print("[DB] Factory database ready.")

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS defect_reports (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT,
                line_number TEXT,
                description TEXT,
                status      TEXT DEFAULT 'open'
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   TEXT,
                machine_id  TEXT,
                issue       TEXT,
                priority    TEXT DEFAULT 'normal',
                status      TEXT DEFAULT 'pending'
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS production_log (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT,
                line_number     TEXT,
                units_completed INTEGER,
                shift           TEXT
            )
        """)
        self.conn.commit()

    def log_defect(self, line_number, description):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO defect_reports (timestamp, line_number, description) VALUES (?,?,?)",
            (datetime.datetime.now().isoformat(), line_number, description)
        )
        self.conn.commit()
        return c.lastrowid

    def log_maintenance(self, machine_id, issue, priority="normal"):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO maintenance_requests (timestamp, machine_id, issue, priority) VALUES (?,?,?,?)",
            (datetime.datetime.now().isoformat(), machine_id, issue, priority)
        )
        self.conn.commit()
        return c.lastrowid

    def get_defects_today(self):
        c = self.conn.cursor()
        c.execute("""
            SELECT id, line_number, description, timestamp
            FROM defect_reports
            WHERE DATE(timestamp) = DATE('now')
            ORDER BY timestamp DESC
        """)
        return c.fetchall()

    def get_production_count(self, line_number=None):
        c = self.conn.cursor()
        if line_number:
            c.execute("""
                SELECT COALESCE(SUM(units_completed), 0)
                FROM production_log
                WHERE line_number = ? AND DATE(timestamp) = DATE('now')
            """, (line_number,))
        else:
            c.execute("""
                SELECT COALESCE(SUM(units_completed), 0)
                FROM production_log
                WHERE DATE(timestamp) = DATE('now')
            """)
        return c.fetchone()[0]


# ══════════════════════════════════════════════════════════════
# MAIN ASSISTANT CLASS
# ══════════════════════════════════════════════════════════════
class SimpleVirtualAssistant:

    def __init__(self, name="Assistant"):
        print("\n" + "="*70)
        print(f"VIRTUAL ASSISTANT: {name}")
        print("="*70)

        self.name = name

        # UPGRADE 3: Session log list — stores every command
        self.session_log = []

        # Original history list (keep it)
        self.task_history = []

        # UPGRADE 5: Context memory — remembers last command
        self.context = {
            "last_intent":       None,
            "last_command":      None,
            "last_search":       None,
            "last_calculation":  None,
            "conversation":      []    # last 5 exchanges
        }

        # UPGRADE 12: Database connection
        self.db = FactoryDatabase()

        # Train the ML model
        print("\n[INFO] Training Intent Classification Model...")
        self.train_intent_classifier()
        print("[SUCCESS] Model trained successfully!")

    # ──────────────────────────────────────────
    # TRAINING DATA
    # ──────────────────────────────────────────
    def train_intent_classifier(self):
        """
        Train ML model to classify user intents.
        
        HOW TO ADD NEW INTENTS:
        1. Add examples inside training_data below
        2. Add a handler method (def handle_xxx)
        3. Add elif branch in execute_task()
        That's it — 3 steps!
        """

        training_data = [

            # ── ORIGINAL INTENTS ──────────────────

            # TIME
            ("what time is it",            "time"),
            ("tell me the time",            "time"),
            ("current time please",         "time"),
            ("what's the time",             "time"),
            ("time now",                    "time"),
            ("show me the current time",    "time"),   # UPGRADE 1: extra examples
            ("could you tell me the time",  "time"),
            ("what hour is it",             "time"),
            ("I need to know the time",     "time"),
            ("time please",                 "time"),

            # DATE
            ("what's the date today",       "date"),
            ("tell me today's date",        "date"),
            ("what day is it",              "date"),
            ("current date",                "date"),
            ("today's date",                "date"),
            ("what is today's date",        "date"),   # UPGRADE 1
            ("tell me the date",            "date"),

            # SEARCH
            ("search for machine learning", "search"),
            ("google python programming",   "search"),
            ("look up artificial intelligence","search"),
            ("find information about deep learning","search"),
            ("search neural networks",      "search"),
            ("web search for data science", "search"),
            ("find me tutorials on AI",     "search"),
            ("search the web for",          "search"),  # UPGRADE 1

            # GREETING
            ("hello",                       "greeting"),
            ("hi there",                    "greeting"),
            ("hey",                         "greeting"),
            ("good morning",                "greeting"),
            ("good evening",                "greeting"),
            ("good afternoon",              "greeting"),  # UPGRADE 1

            # CALCULATE
            ("calculate 5 plus 3",          "calculate"),
            ("what is 10 times 2",          "calculate"),
            ("compute 100 divided by 5",    "calculate"),
            ("solve 7 minus 3",             "calculate"),
            ("add 15 and 25",               "calculate"),
            ("multiply 12 by 8",            "calculate"),  # UPGRADE 1
            ("subtract 9 from 20",          "calculate"),

            # JOKE
            ("tell me a joke",              "joke"),
            ("make me laugh",               "joke"),
            ("say something funny",         "joke"),
            ("joke please",                 "joke"),
            ("got any jokes",               "joke"),

            # WEATHER
            ("what's the weather",          "weather"),
            ("weather forecast",            "weather"),
            ("how's the weather today",     "weather"),
            ("weather in seoul",            "weather"),  # UPGRADE 1
            ("is it going to rain",         "weather"),

            # FAREWELL
            ("goodbye",                     "farewell"),
            ("bye",                         "farewell"),
            ("see you later",               "farewell"),
            ("exit",                        "farewell"),
            ("quit",                        "farewell"),

            # HELP
            ("help me",                     "help"),
            ("what can you do",             "help"),
            ("show me commands",            "help"),
            ("list commands",               "help"),     # UPGRADE 1

            # ── UPGRADE 4: AJIN FACTORY INTENTS ──────────

            # DEFECT REPORTING
            ("report defect on line 3",                 "report_defect"),
            ("quality issue at station 5",              "report_defect"),
            ("defect found at assembly point 2",        "report_defect"),
            ("log a problem on line 1",                 "report_defect"),
            ("there is a welding gap on door panel",    "report_defect"),
            ("paint defect on unit 47",                 "report_defect"),
            ("alignment issue at station 3",            "report_defect"),
            ("record quality problem line 2",           "report_defect"),
            ("defect report for machine 6",             "report_defect"),
            ("log manufacturing error at point 4",      "report_defect"),

            # STATUS CHECK
            ("what is the status of line 2",            "check_status"),
            ("show production count today",             "check_status"),
            ("how many units completed on line 3",      "check_status"),
            ("current production numbers",              "check_status"),
            ("line 4 output today",                     "check_status"),
            ("total units this shift",                  "check_status"),
            ("production status report",                "check_status"),
            ("check line 1 progress",                   "check_status"),
            ("how is line 2 performing",                "check_status"),
            ("daily production summary",                "check_status"),

            # MAINTENANCE REQUEST
            ("request maintenance for machine 7",       "maintenance"),
            ("machine 3 needs repair",                  "maintenance"),
            ("call technician to station 6",            "maintenance"),
            ("maintenance alert for conveyor belt",     "maintenance"),
            ("machine 5 is making strange noises",      "maintenance"),
            ("send maintenance to line 2",              "maintenance"),
            ("emergency repair needed at station 4",    "maintenance"),

            # SHIFT LOG
            ("log shift handover notes",                "shift_log"),
            ("save end of shift report",                "shift_log"),
            ("record shift summary",                    "shift_log"),
            ("write shift notes",                       "shift_log"),
            ("shift change report",                     "shift_log"),

            # EMAIL ALERT  ← UPGRADE 8
            ("send email to manager",                   "send_email"),
            ("email the supervisor",                    "send_email"),
            ("notify manager by email",                 "send_email"),
            ("send alert email",                        "send_email"),
        ]

        # Separate commands and intents
        commands = [item[0] for item in training_data]
        intents  = [item[1] for item in training_data]

        # UPGRADE 6: Use Pipeline with Logistic Regression
        # (replaces the old TfidfVectorizer + MultinomialNB)
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=500,      # was 100, now 500
                ngram_range=(1, 2),    # NEW: captures word pairs
                sublinear_tf=True,     # NEW: smoother frequencies
                min_df=1
            )),
            ('clf', LogisticRegression(
                C=5.0,
                max_iter=1000,
                random_state=42
            ))
        ])

        self.pipeline.fit(commands, intents)

        accuracy = self.pipeline.score(commands, intents)
        print(f"   ├─ Training examples : {len(training_data)}")
        print(f"   ├─ Unique intents    : {len(set(intents))}")
        print(f"   └─ Training accuracy : {accuracy*100:.2f}%")

    # ──────────────────────────────────────────
    # PREDICT INTENT
    # ──────────────────────────────────────────
    def predict_intent(self, command):
        """Predict intent and return (intent, confidence)"""
        # UPGRADE 6: use pipeline instead of separate vectorizer + model
        intent     = self.pipeline.predict([command])[0]
        proba      = self.pipeline.predict_proba([command])[0]
        confidence = max(proba)
        return intent, confidence

    # ──────────────────────────────────────────
    # RESPOND
    # ──────────────────────────────────────────
    def respond(self, message):
        print(f"\n{self.name}: {message}")

    # ──────────────────────────────────────────
    # UPGRADE 3: SESSION LOGGING
    # Called inside process_command automatically
    # ──────────────────────────────────────────
    def _log_session(self, command, intent, confidence):
        entry = {
            "time":       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command":    command,
            "intent":     intent,
            "confidence": round(confidence * 100, 1)
        }
        self.session_log.append(entry)

        # Save to file
        with open("session_log.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ──────────────────────────────────────────
    # UPGRADE 5: CONTEXT UPDATER
    # Called inside process_command automatically
    # ──────────────────────────────────────────
    def _update_context(self, intent, command):
        self.context["last_intent"]  = intent
        self.context["last_command"] = command

        if intent == "search":
            q = re.sub(r'search for|google|look up|find', '', command).strip()
            self.context["last_search"] = q

        if intent == "calculate":
            self.context["last_calculation"] = command

        self.context["conversation"].append({"intent": intent, "command": command})
        if len(self.context["conversation"]) > 5:
            self.context["conversation"].pop(0)

    # ──────────────────────────────────────────
    # PROCESS COMMAND — MAIN ENTRY POINT
    # ──────────────────────────────────────────
    def process_command(self, command):
        if not command or not command.strip():
            return True

        command = command.lower().strip()

        # UPGRADE 5: Check for follow-up phrases first
        followups = ["again", "repeat that", "same thing", "do it again"]
        if any(p in command for p in followups):
            if self.context["last_intent"]:
                self.respond(f"Repeating: {self.context['last_command']}")
                return self.execute_task(
                    self.context["last_intent"],
                    self.context["last_command"]
                )

        # Predict intent
        intent, confidence = self.predict_intent(command)

        # UPGRADE 2: Confidence threshold check
        n_classes = len(self.pipeline.classes_)
        normalized_conf = (confidence - 1/n_classes) / (1 - 1/n_classes)

        if normalized_conf < 0.25:
            self.respond(
                f"I'm not sure I understood. "
                f"Could you rephrase? (confidence was {confidence*100:.0f}%)"
            )
            self._log_session(command, "UNKNOWN", normalized_conf)
            return True

        elif normalized_conf < 0.45:
            self.respond(
                f"Did you mean to {intent.replace('_',' ')}? "
                f"Type 'yes' to confirm or rephrase."
            )
            confirm = input("You: ").lower().strip()
            if "yes" not in confirm:
                self.respond("Cancelled. Please try again.")
                return True

        # Show what was detected
        print(f"\n[ML] Intent: {intent.upper()}  |  "
              f"Confidence: {confidence*100:.1f}%")

        # UPGRADE 3: Log this command
        self._log_session(command, intent, confidence)

        # UPGRADE 5: Update context
        self._update_context(intent, command)

        # Also log to task history (original)
        self.task_history.append({
            "command":   command,
            "intent":    intent,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

        return self.execute_task(intent, command)

    # ──────────────────────────────────────────
    # EXECUTE TASK — ADD NEW INTENTS HERE
    # ──────────────────────────────────────────
    def execute_task(self, intent, command):
        """
        Routes to the correct handler.
        
        TO ADD A NEW INTENT:
        Add:   elif intent == "your_new_intent":
                   self.handle_your_new_intent(command)
        """

        # ── ORIGINAL INTENTS ──────────────────

        if intent == "time":
            self.handle_time()

        elif intent == "date":
            self.handle_date()

        elif intent == "search":
            self.handle_search(command)

        elif intent == "greeting":
            self.handle_greeting()

        elif intent == "calculate":
            self.handle_calculate(command)

        elif intent == "joke":
            self.handle_joke()

        elif intent == "weather":
            self.handle_weather(command)   # UPGRADE 7: now calls real API

        elif intent == "farewell":
            self.respond("Goodbye! Have a great day!")
            return False

        elif intent == "help":
            self.handle_help()

        # ── UPGRADE 4: AJIN FACTORY INTENTS ──

        elif intent == "report_defect":
            self.handle_report_defect(command)

        elif intent == "check_status":
            self.handle_check_status(command)

        elif intent == "maintenance":
            self.handle_maintenance(command)

        elif intent == "shift_log":
            self.handle_shift_log(command)

        # ── UPGRADE 8: EMAIL ──────────────────

        elif intent == "send_email":
            self.handle_send_email(command)

        else:
            self.respond(
                "I don't know how to handle that yet. "
                "Type 'help' to see what I can do."
            )

        return True

    # ══════════════════════════════════════════
    # HANDLERS — ONE METHOD PER INTENT
    # ══════════════════════════════════════════

    # ── ORIGINAL HANDLERS ─────────────────────

    def handle_time(self):
        t = datetime.datetime.now().strftime("%I:%M %p")
        self.respond(f"The current time is {t}")

    def handle_date(self):
        d   = datetime.datetime.now().strftime("%B %d, %Y")
        day = datetime.datetime.now().strftime("%A")
        self.respond(f"Today is {day}, {d}")

    def handle_search(self, command):
        query = re.sub(
            r'search for|search|google|look up|find information about|find',
            '', command
        ).strip()
        if query:
            self.respond(f"Searching for: {query}")
            print(f"[ACTION] Opening: https://google.com/search?q={query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            self.respond("What would you like to search for?")

    def handle_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            g = "Good morning"
        elif hour < 18:
            g = "Good afternoon"
        else:
            g = "Good evening"
        self.respond(f"{g}! How can I assist you?")

    def handle_calculate(self, command):
        try:
            expr = command
            replacements = {
                "plus":        "+",
                "add":         "+",
                "minus":       "-",
                "subtract":    "-",
                "times":       "*",
                "multiply":    "*",
                "multiplied by":"*",
                "divided by":  "/",
                "divide":      "/",
                "what is":     "",
                "calculate":   "",
                "compute":     "",
                "solve":       "",
            }
            for word, symbol in replacements.items():
                expr = expr.replace(word, symbol)

            expr = re.sub(r'[^0-9+\-*/().]', ' ', expr)
            expr = ' '.join(expr.split())

            if expr:
                result = eval(expr)
                self.respond(f"The answer is {result}")
            else:
                self.respond("Please say the numbers clearly, e.g. 'calculate 5 plus 3'")

        except Exception:
            self.respond("Sorry, I couldn't calculate that. Try: 'calculate 10 plus 5'")

    def handle_joke(self):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the ML model go to therapy? It had too many issues with its training data!",
            "How many data scientists does it take to change a light bulb? Just one, but they need 10,000 examples first!",
            "Why did the AI break up with Machine Learning? It needed more deep learning in the relationship!",
            "What's a programmer's favorite place? The Foo Bar!",
        ]
        self.respond(random.choice(jokes))

    def handle_help(self):
        help_text = """
╔══════════════════════════════════════════════════════╗
║              AVAILABLE COMMANDS                       ║
╠══════════════════════════════════════════════════════╣
║  GENERAL                                             ║
║   "what time is it"                                  ║
║   "what's the date"                                  ║
║   "tell me a joke"                                   ║
║   "calculate 15 plus 27"                             ║
║   "search for [topic]"                               ║
║   "weather in [city]"                                ║
║                                                      ║
║  FACTORY (Ajin Industry)                             ║
║   "report defect on line 3"                          ║
║   "check status of line 2"                           ║
║   "request maintenance for machine 7"               ║
║   "log shift handover notes"                         ║
║   "send email to manager"                            ║
╚══════════════════════════════════════════════════════╝
        """
        print(help_text)

    # ── UPGRADE 7: REAL WEATHER API ──────────
    # Replace the old fake weather handler

    def handle_weather(self, command):
        # Extract city from command
        city = re.sub(
            r"weather in|weather for|what's the weather in|"
            r"how's the weather in|weather",
            '', command
        ).strip()
        city = city or "Seoul"   # Default city

        try:
            # Free API key from openweathermap.org
            API_KEY = "YOUR_FREE_API_KEY_HERE"

            response = requests.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={
                    "q":     city,
                    "appid": API_KEY,
                    "units": "metric"
                },
                timeout=5
            )

            if response.status_code == 200:
                data        = response.json()
                temp        = data['main']['temp']
                feels_like  = data['main']['feels_like']
                description = data['weather'][0]['description']
                humidity    = data['main']['humidity']

                self.respond(
                    f"Weather in {city}: {description}. "
                    f"Temperature {temp:.0f}°C, feels like {feels_like:.0f}°C. "
                    f"Humidity {humidity}%."
                )
            else:
                self.respond(f"Couldn't find weather for '{city}'. Check the city name.")

        except requests.exceptions.ConnectionError:
            self.respond(
                "No internet connection. "
                "For offline use, connect to a local weather database."
            )
        except Exception as e:
            self.respond(f"Weather service error: {e}")

    # ── UPGRADE 4: AJIN FACTORY HANDLERS ─────

    def handle_report_defect(self, command):
        """Save defect report to database"""
        # Extract line number if mentioned
        line_match = re.search(r'line\s*(\d+)', command)
        station_match = re.search(r'station\s*(\d+)', command)

        if line_match:
            location = f"Line {line_match.group(1)}"
        elif station_match:
            location = f"Station {station_match.group(1)}"
        else:
            location = "Location unspecified"

        # Save to database  ← UPGRADE 12
        report_id = self.db.log_defect(location, command)

        # Also save to text file as backup
        with open("defect_reports.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] ID:{report_id} | {location} | {command}\n")

        self.respond(
            f"Defect report saved. "
            f"Report ID: {report_id}. "
            f"Location: {location}. "
            f"Timestamp: {datetime.datetime.now().strftime('%H:%M:%S')}."
        )

    def handle_check_status(self, command):
        """Check production status"""
        line_match = re.search(r'line\s*(\d+)', command)

        if line_match:
            line_num = line_match.group(1)
            # Try to get from database first  ← UPGRADE 12
            count = self.db.get_production_count(line_number=line_num)
            if count > 0:
                self.respond(
                    f"Line {line_num} has completed {count} units today."
                )
            else:
                # Fallback: simulated data
                simulated = random.randint(400, 900)
                self.respond(
                    f"Line {line_num} status: approximately "
                    f"{simulated} units completed this shift. "
                    f"(Connect to PO system for real data.)"
                )
        else:
            total = self.db.get_production_count()
            if total > 0:
                self.respond(f"Total production today: {total} units.")
            else:
                simulated = random.randint(2000, 4000)
                self.respond(
                    f"Estimated production today: {simulated} units. "
                    f"(Connect to PO system for real data.)"
                )

    def handle_maintenance(self, command):
        """Log maintenance request"""
        machine_match = re.search(r'machine\s*(\d+)', command)
        station_match = re.search(r'station\s*(\d+)', command)

        if machine_match:
            machine = f"Machine {machine_match.group(1)}"
        elif station_match:
            machine = f"Station {station_match.group(1)}"
        else:
            machine = "Machine unspecified"

        # Detect priority
        priority = "urgent" if any(
            w in command for w in ["emergency", "urgent", "critical", "immediately"]
        ) else "normal"

        # Save to database  ← UPGRADE 12
        ticket_id = self.db.log_maintenance(machine, command, priority)

        # Save to file too
        with open("maintenance_requests.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(
                f"[{timestamp}] TICKET:{ticket_id} | {machine} | "
                f"Priority:{priority} | {command}\n"
            )

        self.respond(
            f"Maintenance request submitted. "
            f"Ticket ID: {ticket_id}. "
            f"Machine: {machine}. "
            f"Priority: {priority}."
        )

    def handle_shift_log(self, command):
        """Save shift log entry"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shift = (
            "Morning"   if datetime.datetime.now().hour < 14 else
            "Afternoon" if datetime.datetime.now().hour < 22 else
            "Night"
        )

        entry = f"[{timestamp}] Shift: {shift} | Notes: {command}\n"

        with open("shift_logs.txt", "a") as f:
            f.write(entry)

        self.respond(
            f"Shift log saved. "
            f"Shift: {shift}. "
            f"Time: {timestamp}."
        )

    # ── UPGRADE 8: EMAIL ──────────────────────

    def handle_send_email(self, command):
        """
        Send email alert.
        SETUP: Fill in your email credentials below.
        For Gmail: enable 2FA and create an App Password.
        """
        SENDER_EMAIL   = "your.email@gmail.com"
        SENDER_PASS    = "your_app_password_here"
        RECEIVER_EMAIL = "manager@company.com"

        subject = "Factory Alert from Virtual Assistant"
        body    = (
            f"Automated alert from Virtual Assistant.\n\n"
            f"Command received: {command}\n"
            f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        try:
            msg = MIMEMultipart()
            msg['From']    = SENDER_EMAIL
            msg['To']      = RECEIVER_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)
            server.quit()

            self.respond(f"Email alert sent to {RECEIVER_EMAIL} successfully.")

        except smtplib.SMTPAuthenticationError:
            self.respond(
                "Email credentials not configured. "
                "Please set your email and app password in handle_send_email()."
            )
        except Exception as e:
            self.respond(f"Could not send email: {e}")

    # ──────────────────────────────────────────
    # UPGRADE 3: SESSION STATISTICS
    # ──────────────────────────────────────────
    def show_statistics(self):
        if not self.session_log:
            print("\n[STATS] No commands yet in this session.")
            return

        print("\n" + "="*70)
        print("SESSION STATISTICS")
        print("="*70)

        total    = len(self.session_log)
        avg_conf = sum(e["confidence"] for e in self.session_log) / total
        intents  = Counter(e["intent"] for e in self.session_log)

        print(f"\nTotal commands     : {total}")
        print(f"Average confidence : {avg_conf:.1f}%")
        print(f"\nIntent breakdown:")
        for intent, count in intents.most_common():
            bar = "█" * count
            print(f"  {intent:<20} {bar} ({count})")

    # ──────────────────────────────────────────
    # MAIN RUN LOOP — unchanged from original
    # ──────────────────────────────────────────
    def run(self):
        print("\n" + "="*70)
        print("ASSISTANT READY — Type your commands")
        print("Type 'exit' to quit  |  Type 'stats' for session summary")
        print("="*70)

        while True:
            try:
                command = input("\nYou: ").strip()

                if not command:
                    continue

                # UPGRADE 3: Show stats on demand
                if command.lower() == "stats":
                    self.show_statistics()
                    continue

                result = self.process_command(command)
                if not result:
                    break

            except KeyboardInterrupt:
                print("\n[Interrupted]")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")

        self.show_statistics()
        print("\n" + "="*70)
        print("SESSION ENDED")
        print("="*70)


# ──────────────────────────────────────────
# ENTRY POINT — bottom of file, unchanged
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\nChoose mode:")
    print("  1. Chat with assistant")
    print("  2. Quick demo (automated)")

    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "2":
        assistant = SimpleVirtualAssistant(name="Demo")
        demo_commands = [
            "hello",
            "what time is it",
            "calculate 25 plus 17",
            "report defect on line 3",
            "check status of line 2",
            "request maintenance for machine 7",
            "tell me a joke",
            "goodbye"
        ]
        print("\n" + "="*70)
        print("AUTOMATED DEMO")
        print("="*70)
        for cmd in demo_commands:
            print(f"\n{'─'*70}")
            input(f"Press ENTER to run: '{cmd}'")
            assistant.process_command(cmd)
        assistant.show_statistics()
    else:
        assistant = SimpleVirtualAssistant(name="Assistant")
        assistant.run()
