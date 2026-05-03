"""
Virtual Personal Assistant with Machine Learning
Complete implementation with voice recognition, NLP, and task automation
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class VirtualAssistant:
    """
    A comprehensive virtual assistant with:
    - Speech recognition (voice input)
    - Text-to-speech (voice output)
    - Intent classification using ML
    - Task execution capabilities
    """
    
    def __init__(self, name="Assistant"):
        """
        Step 1: Initialize the Virtual Assistant
        
        Components initialized:
        - Speech recognizer: Converts speech to text
        - Text-to-speech engine: Converts text to speech
        - Intent classifier: ML model to understand user commands
        - Task handlers: Functions to execute different tasks
        """
        print("\n" + "="*60)
        print("INITIALIZING VIRTUAL ASSISTANT")
        print("="*60)
        
        self.name = name
        
        # Speech Recognition Setup
        print("\n1. Setting up Speech Recognition...")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-Speech Setup
        print("2. Setting up Text-to-Speech Engine...")
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and set to a clear one
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)  # Usually female voice
        
        # Intent Classification Model
        print("3. Training Intent Classification Model...")
        self.vectorizer = None
        self.intent_model = None
        self.train_intent_classifier()
        
        # Task execution history
        self.task_history = []
        
        print("\n✓ Virtual Assistant initialized successfully!")
        self.speak(f"Hello! I am {self.name}. How can I help you today?")
    
    def train_intent_classifier(self):
        """
        Step 2: Train Machine Learning Model for Intent Classification
        
        What is Intent Classification?
        - Understanding what the user wants to do
        - Example: "What time is it?" → Intent: GET_TIME
        - Example: "Search for Python tutorials" → Intent: WEB_SEARCH
        
        How it works:
        1. Create training data with examples of different intents
        2. Convert text to numerical features (TF-IDF)
        3. Train a Naive Bayes classifier
        4. Use the model to predict intent of new commands
        """
        
        # Training data: (command example, intent label)
        training_data = [
            # TIME related
            ("what time is it", "time"),
            ("tell me the time", "time"),
            ("current time please", "time"),
            ("what's the time", "time"),
            
            # DATE related
            ("what's the date today", "date"),
            ("tell me today's date", "date"),
            ("what day is it", "date"),
            ("current date", "date"),
            
            # WEB SEARCH related
            ("search for machine learning", "search"),
            ("google python programming", "search"),
            ("look up artificial intelligence", "search"),
            ("find information about deep learning", "search"),
            ("search neural networks", "search"),
            
            # OPEN APPLICATION related
            ("open browser", "open_app"),
            ("launch notepad", "open_app"),
            ("start calculator", "open_app"),
            ("open youtube", "open_app"),
            
            # WEATHER related
            ("what's the weather", "weather"),
            ("weather forecast", "weather"),
            ("how's the weather today", "weather"),
            ("is it going to rain", "weather"),
            
            # GREETING related
            ("hello", "greeting"),
            ("hi there", "greeting"),
            ("hey", "greeting"),
            ("good morning", "greeting"),
            ("good evening", "greeting"),
            
            # FAREWELL related
            ("goodbye", "farewell"),
            ("bye", "farewell"),
            ("see you later", "farewell"),
            ("exit", "farewell"),
            ("quit", "farewell"),
            
            # HELP related
            ("help me", "help"),
            ("what can you do", "help"),
            ("show me commands", "help"),
            ("assistance needed", "help"),
            
            # JOKE related
            ("tell me a joke", "joke"),
            ("make me laugh", "joke"),
            ("say something funny", "joke"),
            
            # CALCULATION related
            ("calculate 5 plus 3", "calculate"),
            ("what is 10 times 2", "calculate"),
            ("compute 100 divided by 5", "calculate"),
            ("solve 7 minus 3", "calculate"),
            
            # NOTE related
            ("take a note", "note"),
            ("remember this", "note"),
            ("write this down", "note"),
            ("save a note", "note"),
            
            # REMINDER related
            ("set a reminder", "reminder"),
            ("remind me to", "reminder"),
            ("create reminder", "reminder"),
        ]
        
        # Separate commands and intents
        commands = [item[0] for item in training_data]
        intents = [item[1] for item in training_data]
        
        # Feature Extraction: Convert text to TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=100)
        X = self.vectorizer.fit_transform(commands)
        
        # Train the classifier
        self.intent_model = MultinomialNB()
        self.intent_model.fit(X, intents)
        
        # Calculate training accuracy
        train_accuracy = self.intent_model.score(X, intents)
        print(f"   Intent Classifier trained with {len(training_data)} examples")
        print(f"   Training accuracy: {train_accuracy*100:.2f}%")
    
    def speak(self, text):
        """
        Step 3: Text-to-Speech Output
        
        Converts text to speech and plays it through speakers
        Also prints the text to console for visibility
        """
        print(f"\n{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """
        Step 4: Speech-to-Text Input
        
        How it works:
        1. Listen to microphone input
        2. Use Google Speech Recognition API
        3. Convert audio to text
        4. Handle errors (no speech, unclear audio, etc.)
        
        Returns:
        - The recognized text (string)
        - None if recognition failed
        """
        with self.microphone as source:
            print("\nListening...")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("Recognizing...")
                # Convert speech to text using Google's API
                command = self.recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()
                
            except sr.WaitTimeoutError:
                print("No speech detected")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                self.speak("Sorry, I didn't catch that. Could you repeat?")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                self.speak("Sorry, my speech recognition service is unavailable")
                return None
    
    def predict_intent(self, command):
        """
        Step 5: Intent Classification using ML
        
        Takes a user command and predicts what they want to do
        
        Process:
        1. Convert command to TF-IDF features (same as training)
        2. Use trained model to predict intent
        3. Get confidence score
        
        Returns:
        - intent: The predicted intent (string)
        - confidence: How confident the model is (0-1)
        """
        # Vectorize the command
        command_vector = self.vectorizer.transform([command])
        
        # Predict intent
        intent = self.intent_model.predict(command_vector)[0]
        
        # Get confidence (probability of predicted class)
        probabilities = self.intent_model.predict_proba(command_vector)[0]
        confidence = max(probabilities)
        
        return intent, confidence
    
    def execute_task(self, intent, command):
        """
        Step 6: Task Execution
        
        Based on the predicted intent, execute the appropriate task
        This is where the assistant actually does things!
        """
        # Log the task
        self.task_history.append({
            'command': command,
            'intent': intent,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Route to appropriate handler
        if intent == "time":
            self.tell_time()
        
        elif intent == "date":
            self.tell_date()
        
        elif intent == "search":
            self.web_search(command)
        
        elif intent == "open_app":
            self.open_application(command)
        
        elif intent == "weather":
            self.tell_weather()
        
        elif intent == "greeting":
            self.greet()
        
        elif intent == "farewell":
            return self.say_goodbye()
        
        elif intent == "help":
            self.show_help()
        
        elif intent == "joke":
            self.tell_joke()
        
        elif intent == "calculate":
            self.calculate(command)
        
        elif intent == "note":
            self.take_note(command)
        
        elif intent == "reminder":
            self.set_reminder(command)
        
        else:
            self.speak("I'm not sure how to handle that yet. Try asking for help.")
        
        return True
    
    # ==================== TASK HANDLERS ====================
    
    def tell_time(self):
        """Get and speak the current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {current_time}")
    
    def tell_date(self):
        """Get and speak the current date"""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        day_of_week = datetime.datetime.now().strftime("%A")
        self.speak(f"Today is {day_of_week}, {current_date}")
    
    def web_search(self, command):
        """
        Perform a web search
        Extracts search query from command and opens browser
        """
        # Extract search query
        # Remove common phrases to get the actual search term
        search_query = command.replace("search for", "").replace("search", "")
        search_query = search_query.replace("google", "").replace("look up", "")
        search_query = search_query.replace("find information about", "").strip()
        
        if search_query:
            self.speak(f"Searching for {search_query}")
            url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(url)
        else:
            self.speak("What would you like me to search for?")
    
    def open_application(self, command):
        """Open applications based on command"""
        if "browser" in command or "chrome" in command:
            self.speak("Opening browser")
            webbrowser.open("https://www.google.com")
        
        elif "youtube" in command:
            self.speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        
        elif "calculator" in command:
            self.speak("Opening calculator")
            os.system("calc")  # Windows calculator
        
        elif "notepad" in command:
            self.speak("Opening notepad")
            os.system("notepad")  # Windows notepad
        
        else:
            self.speak("I'm not sure which application you want to open")
    
    def tell_weather(self):
        """
        Weather information
        In a real implementation, this would call a weather API
        """
        self.speak("For real-time weather, I would need to be connected to a weather API. "
                  "Would you like me to search for weather information online?")
    
    def greet(self):
        """Respond to greetings"""
        hour = datetime.datetime.now().hour
        
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        self.speak(f"{greeting}! How can I assist you today?")
    
    def say_goodbye(self):
        """Say goodbye and exit"""
        self.speak("Goodbye! Have a great day!")
        return False  # Signal to stop the assistant
    
    def show_help(self):
        """Display available commands"""
        help_text = """
        I can help you with:
        - Tell the time and date
        - Search the web
        - Open applications like browser or calculator
        - Tell jokes
        - Perform calculations
        - Take notes
        - Set reminders
        
        Just speak naturally and I'll try to understand!
        """
        self.speak("Here's what I can do for you.")
        print(help_text)
    
    def tell_joke(self):
        """Tell a random joke"""
        jokes = [
            "Why did the machine learning model go to therapy? It had too many issues with its training data!",
            "What's a programmer's favorite place? The Foo Bar!",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
            "Why did the AI break up with machine learning? It needed more deep learning in the relationship!"
        ]
        import random
        joke = random.choice(jokes)
        self.speak(joke)
    
    def calculate(self, command):
        """
        Perform basic calculations
        Extracts numbers and operations from command
        """
        try:
            # Extract mathematical expression
            # Replace words with symbols
            expression = command.replace("plus", "+").replace("minus", "-")
            expression = expression.replace("times", "*").replace("multiplied by", "*")
            expression = expression.replace("divided by", "/").replace("divide", "/")
            
            # Extract numbers and operators
            expression = re.sub(r'[^0-9+\-*/().]', ' ', expression)
            expression = ' '.join(expression.split())
            
            if expression:
                result = eval(expression)
                self.speak(f"The answer is {result}")
            else:
                self.speak("I couldn't understand the calculation. Please try again.")
        
        except Exception as e:
            self.speak("Sorry, I couldn't perform that calculation")
    
    def take_note(self, command):
        """Save a note to a file"""
        # Extract the note content
        note_content = command.replace("take a note", "").replace("remember this", "")
        note_content = note_content.replace("write this down", "").strip()
        
        if note_content:
            # Save to file
            with open("assistant_notes.txt", "a") as file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"[{timestamp}] {note_content}\n")
            
            self.speak("Note saved successfully")
        else:
            self.speak("What would you like me to remember?")
    
    def set_reminder(self, command):
        """
        Set a reminder
        In a full implementation, this would schedule actual reminders
        """
        reminder_text = command.replace("set a reminder", "").replace("remind me to", "")
        reminder_text = reminder_text.strip()
        
        if reminder_text:
            # Save reminder
            with open("assistant_reminders.txt", "a") as file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"[{timestamp}] {reminder_text}\n")
            
            self.speak(f"Reminder set: {reminder_text}")
        else:
            self.speak("What should I remind you about?")
    
    def process_text_command(self, command):
        """
        Process a text command (for testing without voice)
        
        This is useful for:
        - Testing the assistant without microphone
        - Debugging intent classification
        - Running in environments without audio
        """
        if not command:
            return True
        
        print(f"\nYou: {command}")
        
        # Predict intent
        intent, confidence = self.predict_intent(command)
        print(f"Detected Intent: {intent} (Confidence: {confidence*100:.2f}%)")
        
        # Execute task
        return self.execute_task(intent, command)
    
    def run_voice_mode(self):
        """
        Step 7: Main Voice Interaction Loop
        
        Continuously:
        1. Listen for voice commands
        2. Classify intent
        3. Execute tasks
        4. Repeat until user says goodbye
        """
        self.speak("Voice mode activated. I'm listening...")
        
        while True:
            # Listen for command
            command = self.listen()
            
            if command:
                # Predict intent
                intent, confidence = self.predict_intent(command)
                print(f"Detected Intent: {intent} (Confidence: {confidence*100:.2f}%)")
                
                # Execute task
                continue_running = self.execute_task(intent, command)
                
                if not continue_running:
                    break
    
    def run_text_mode(self):
        """
        Step 8: Text-based Interaction (for testing)
        
        Allows testing without voice input
        Useful for development and debugging
        """
        print("\n" + "="*60)
        print("TEXT MODE - Type your commands")
        print("Type 'exit' to quit")
        print("="*60)
        
        while True:
            command = input("\nYou: ").lower().strip()
            
            if command in ['exit', 'quit', 'goodbye', 'bye']:
                self.say_goodbye()
                break
            
            if command:
                continue_running = self.process_text_command(command)
                if not continue_running:
                    break
    
    def show_task_history(self):
        """Display the history of executed tasks"""
        print("\n" + "="*60)
        print("TASK HISTORY")
        print("="*60)
        
        if not self.task_history:
            print("No tasks executed yet.")
        else:
            for i, task in enumerate(self.task_history, 1):
                print(f"\n{i}. {task['timestamp']}")
                print(f"   Command: {task['command']}")
                print(f"   Intent: {task['intent']}")


def demo_mode():
    """
    Step 9: Demo Mode - Showcase all features
    
    Runs through various commands to demonstrate capabilities
    """
    print("\n" + "="*60)
    print("DEMO MODE - Showcasing Virtual Assistant Capabilities")
    print("="*60)
    
    assistant = VirtualAssistant(name="Demo Assistant")
    
    # Demo commands
    demo_commands = [
        "what time is it",
        "what's the date today",
        "hello",
        "tell me a joke",
        "calculate 15 plus 27",
        "search for machine learning tutorials",
        "help me",
        "goodbye"
    ]
    
    print("\n" + "="*60)
    print("RUNNING DEMO COMMANDS")
    print("="*60)
    
    for command in demo_commands:
        print("\n" + "-"*60)
        input(f"Press Enter to run: '{command}'")
        assistant.process_text_command(command)
    
    # Show task history
    assistant.show_task_history()


def interactive_mode():
    """
    Step 10: Interactive Mode - Choose text or voice
    """
    print("\n" + "="*60)
    print("VIRTUAL ASSISTANT - INTERACTIVE MODE")
    print("="*60)
    
    assistant = VirtualAssistant(name="Assistant")
    
    print("\nChoose interaction mode:")
    print("1. Text Mode (type commands)")
    print("2. Voice Mode (speak commands)")
    print("3. Demo Mode (automated showcase)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        assistant.run_text_mode()
    elif choice == "2":
        assistant.run_voice_mode()
    elif choice == "3":
        demo_mode()
    else:
        print("Invalid choice. Starting text mode...")
        assistant.run_text_mode()


if __name__ == "__main__":
    # You can run in different modes:
    
    # Mode 1: Interactive (choose text or voice)
    interactive_mode()
    
    # Mode 2: Direct text mode
    # assistant = VirtualAssistant(name="My Assistant")
    # assistant.run_text_mode()
    
    # Mode 3: Demo mode
    # demo_mode()