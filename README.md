# Virtual Personal Assistant - Quick Start

## Done by Samandar Abdujabbar(Abudjabbarov)

## Project Overview

A complete **Virtual Personal Assistant** powered by Machine Learning that can:
- **Listen** to voice commands (speech recognition)
- **Understand** what you want (ML intent classification)
- **Execute** tasks (web search, calculations, notes, etc.)
- **Respond** with voice output (text-to-speech)

**Think of it as:** Your own mini Siri/Alexa/Google Assistant!

---

## Project Files

### Main Files
- **virtual_assistant.py** - Full version with voice recognition & TTS
- **virtual_assistant_simple.py** - Text-only version (no microphone needed) ⭐ **Start here!**
- **VIRTUAL_ASSISTANT_GUIDE.md** - Complete step-by-step documentation
- **va_requirements.txt** - Python dependencies

---

## Quick Start (3 Simple Steps)

### Step 1: Install Dependencies

```bash
pip install -r va_requirements.txt
```

**Note:** If you encounter issues with `PyAudio`, you can start with the text-only version!

### Step 2: Run the Assistant

**Option A: Text-Only Version (Recommended for Testing)**
```bash
python virtual_assistant_simple.py
```
Choose option 1 for interactive mode, then type commands like:
- "what time is it"
- "calculate 15 plus 27"
- "tell me a joke"
- "help"

**Option B: Full Voice Version (Requires Microphone)**
```bash
python virtual_assistant.py
```

### Step 3: Try It Out!

The assistant understands commands like:
- "What time is it?"
- "What's the date today?"
- "Search for machine learning"
- "Calculate 25 plus 17"
- "Tell me a joke"
- "Take a note"
- "Help"

---

## What You'll Learn

### 1. **Speech Recognition** (Step 4 in code)
```python
def listen(self):
    audio = self.recognizer.listen(source)
    command = self.recognizer.recognize_google(audio)
    return command
```
- Captures audio from microphone
- Sends to Google Speech API
- Converts speech → text

### 2. **Machine Learning Intent Classification** (Step 2 in code)
```python
def train_intent_classifier(self):
    # Training data
    training_data = [
        ("what time is it", "time"),
        ("search for AI", "search"),
    ]
    
    # TF-IDF Vectorization (convert text → numbers)
    self.vectorizer = TfidfVectorizer()
    X = self.vectorizer.fit_transform(commands)
    
    # Train Naive Bayes classifier
    self.model = MultinomialNB()
    self.model.fit(X, intents)
```

**How it works:**
1. **Training data** - Examples of commands + their intents
2. **TF-IDF** - Converts text into numerical features
3. **Naive Bayes** - Learns patterns to classify new commands

**Example:**
- User says: "tell me the current time"
- Model predicts: Intent = "time" (95% confidence)
- Executes: `tell_time()` function

### 3. **Text-to-Speech** (Step 3 in code)
```python
def speak(self, text):
    self.engine.say(text)
    self.engine.runAndWait()
```
- Converts text → spoken audio
- Plays through speakers

### 4. **Task Execution** (Step 6 in code)
```python
def execute_task(self, intent, command):
    if intent == "time":
        self.tell_time()
    elif intent == "search":
        self.web_search(command)
    # ... more tasks
```

---

## How Machine Learning Works Here

### The Flow:

```
User says: "what time is it"
         ↓
Speech Recognition: "what time is it"
         ↓
Text Processing: "what time is it"
         ↓
TF-IDF Vectorization: [0.0, 0.8, 0.0, 0.9, 0.1, ...]
         ↓
Naive Bayes Classifier
         ↓
Predicted Intent: "time" (95% confidence)
         ↓
Execute: tell_time()
         ↓
Response: "The current time is 3:45 PM"
         ↓
Text-to-Speech: 🔊 Audio output
```

### TF-IDF Explained Simply:

**TF-IDF** = Term Frequency × Inverse Document Frequency

- **TF (Term Frequency)**: How often a word appears
- **IDF (Inverse Document Frequency)**: How rare/important a word is

Example:
- Common words like "the", "is" → Low score
- Important words like "time", "search" → High score

This helps the model focus on important words!

### Naive Bayes Explained Simply:

It's a **probability-based** classifier:

```
P(Intent | Command) = P(Command | Intent) × P(Intent) / P(Command)
```

Translation: "What's the probability this command has intent X?"

**Why "Naive"?**
- Assumes all words are independent (naive assumption)
- But it works really well for text classification!

---

## 🛠️ Available Commands

| Category | Example Commands |
|----------|-----------------|
| **Time/Date** | "what time is it", "what's the date" |
| **Search** | "search for python", "google AI" |
| **Calculate** | "calculate 15 plus 27", "what is 10 times 5" |
| **Notes** | "take a note", "remember this" |
| **Fun** | "tell me a joke" |
| **Greetings** | "hello", "hi", "good morning" |
| **Help** | "help", "what can you do" |
| **Exit** | "goodbye", "exit", "quit" |

---

## Demo Modes

### Mode 1: Interactive Chat
```bash
python virtual_assistant_simple.py
# Choose option 1
```
Type commands and get responses

### Mode 2: Automated Demo
```bash
python virtual_assistant_simple.py
# Choose option 2
```
Watch the assistant showcase all features automatically

### Mode 3: Test Intent Classifier
```bash
python virtual_assistant_simple.py
# Choose option 3
```
See how the ML model classifies different commands

---

## Customization

### Add New Intents

**Step 1:** Add training examples in `train_intent_classifier()`
```python
training_data = [
    # Existing data...
    
    # NEW: Email intent
    ("check my email", "email"),
    ("read my messages", "email"),
    ("any new emails", "email"),
]
```

**Step 2:** Create handler function
```python
def check_email(self):
    self.respond("Opening email client")
    webbrowser.open("https://mail.google.com")
```

**Step 3:** Add to router in `execute_task()`
```python
elif intent == "email":
    self.check_email()
```

### Change Voice Settings

```python
# Speech rate (words per minute)
self.engine.setProperty('rate', 150)  # Slower = clearer

# Volume (0.0 to 1.0)
self.engine.setProperty('volume', 0.9)

# Voice (male/female)
voices = self.engine.getProperty('voices')
self.engine.setProperty('voice', voices[1].id)  # Female voice
```

---

## Troubleshooting

### Issue: "PyAudio installation failed"
**Solution:** Use the text-only version:
```bash
python virtual_assistant_simple.py
```

### Issue: "Speech recognition not working"
**Solutions:**
- Check internet connection (Google API needs internet)
- Speak clearly and not too fast
- Check microphone volume
- Reduce background noise

### Issue: "Low accuracy on intent classification"
**Solutions:**
- Add more training examples (currently ~42 examples)
- Add more variations of commands
- Check for typos in training data

---

## Project Architecture

```
┌─────────────────────────────────────────┐
│           USER INTERACTION              │
│                                         │
│  Voice Input → Speech Recognition      │
│                    ↓                    │
│           Text Processing               │
│                    ↓                    │
│        ML Intent Classification         │
│         (TF-IDF + Naive Bayes)         │
│                    ↓                    │
│            Task Execution               │
│         (9+ different handlers)         │
│                    ↓                    │
│           Text-to-Speech                │
│                    ↓                    │
│             Voice Output                │
└─────────────────────────────────────────┘
```

---

## Learning Resources

- **Speech Recognition**: [GitHub - Uberi/speech_recognition](https://github.com/Uberi/speech_recognition)
- **Scikit-learn**: [Official Documentation](https://scikit-learn.org/)
- **TF-IDF Tutorial**: [Towards Data Science](https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76)
- **Naive Bayes**: [StatQuest YouTube](https://www.youtube.com/watch?v=O2L2Uv9pdDA)

---

## Next Steps

### Beginner Level
1. ✅ Run the text-only demo
2. ✅ Add 2-3 new intents
3. ✅ Customize responses

### Intermediate Level
1. Connect to weather API
2. Add email integration
3. Implement wake word detection ("Hey Assistant")
4. Create a GUI interface

### Advanced Level
1. Use deep learning (LSTM/BERT) for better intent classification
2. Add context awareness (remember previous commands)
3. Deploy as a web service (Flask/FastAPI)
4. Add multi-language support
5. Integrate with smart home devices

---

## Key Takeaways

✅ **Speech Recognition**: Convert audio → text using Google API  
✅ **Intent Classification**: Use ML to understand user commands  
✅ **TF-IDF**: Convert text → numbers for ML processing  
✅ **Naive Bayes**: Fast, accurate text classifier  
✅ **Task Automation**: Execute different functions based on intent  
✅ **Text-to-Speech**: Convert responses back to audio  

---

## Success!

You now have a working Virtual Personal Assistant that combines:
- Speech processing
- Machine Learning
- Natural Language Processing
- Task automation

**Try it out and have fun experimenting!** 

---

**Questions or issues?** Check the complete guide in `VIRTUAL_ASSISTANT_GUIDE.md`
