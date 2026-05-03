"""
Virtual Assistant - Text-Only Demo
This version runs without requiring microphone or speakers
Perfect for testing and understanding the ML components
"""

import datetime
import webbrowser
import re
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import warnings
warnings.filterwarnings('ignore')


class SimpleVirtualAssistant:
    """
    Simplified Virtual Assistant - Text Mode Only
    No voice input/output required
    """
    
    def __init__(self, name="Assistant"):
        print("\n" + "="*70)
        print(f"VIRTUAL ASSISTANT: {name}")
        print("="*70)
        
        self.name = name
        self.task_history = []
        
        # Train the intent classifier
        print("\n[INFO] Training Intent Classification Model...")
        self.train_intent_classifier()
        print("[SUCCESS] Model trained successfully!")
    
    def train_intent_classifier(self):
        """
        Train ML model to classify user intents
        """
        # Training data: (command, intent)
        training_data = [
            # TIME
            ("what time is it", "time"),
            ("tell me the time", "time"),
            ("current time please", "time"),
            ("what's the time", "time"),
            ("time now", "time"),
            
            # DATE
            ("what's the date today", "date"),
            ("tell me today's date", "date"),
            ("what day is it", "date"),
            ("current date", "date"),
            ("today's date", "date"),
            
            # SEARCH
            ("search for machine learning", "search"),
            ("google python programming", "search"),
            ("look up artificial intelligence", "search"),
            ("find information about deep learning", "search"),
            ("search neural networks", "search"),
            ("web search for data science", "search"),
            
            # GREETING
            ("hello", "greeting"),
            ("hi there", "greeting"),
            ("hey", "greeting"),
            ("good morning", "greeting"),
            ("good evening", "greeting"),
            
            # FAREWELL
            ("goodbye", "farewell"),
            ("bye", "farewell"),
            ("see you later", "farewell"),
            ("exit", "farewell"),
            ("quit", "farewell"),
            
            # HELP
            ("help me", "help"),
            ("what can you do", "help"),
            ("show me commands", "help"),
            ("assistance needed", "help"),
            
            # JOKE
            ("tell me a joke", "joke"),
            ("make me laugh", "joke"),
            ("say something funny", "joke"),
            ("joke please", "joke"),
            
            # CALCULATE
            ("calculate 5 plus 3", "calculate"),
            ("what is 10 times 2", "calculate"),
            ("compute 100 divided by 5", "calculate"),
            ("solve 7 minus 3", "calculate"),
            ("add 15 and 25", "calculate"),
            
            # WEATHER
            ("what's the weather", "weather"),
            ("weather forecast", "weather"),
            ("how's the weather today", "weather"),
        ]
        
        # Prepare training data
        commands = [item[0] for item in training_data]
        intents = [item[1] for item in training_data]
        
        # TF-IDF Vectorization
        self.vectorizer = TfidfVectorizer(max_features=100)
        X = self.vectorizer.fit_transform(commands)
        
        # Train Naive Bayes
        self.model = MultinomialNB()
        self.model.fit(X, intents)
        
        # Show training info
        accuracy = self.model.score(X, intents)
        print(f"   ├─ Training examples: {len(training_data)}")
        print(f"   ├─ Unique intents: {len(set(intents))}")
        print(f"   └─ Training accuracy: {accuracy*100:.2f}%")
    
    def predict_intent(self, command):
        """
        Predict the intent of a user command
        """
        # Vectorize
        command_vec = self.vectorizer.transform([command])
        
        # Predict
        intent = self.model.predict(command_vec)[0]
        
        # Get confidence
        proba = self.model.predict_proba(command_vec)[0]
        confidence = max(proba)
        
        return intent, confidence
    
    def respond(self, message):
        """Print assistant response"""
        print(f"\n{self.name}: {message}")
    
    def process_command(self, command):
        """
        Main processing function
        """
        if not command or not command.strip():
            return True
        
        command = command.lower().strip()
        
        # Predict intent
        intent, confidence = self.predict_intent(command)
        
        print(f"\n[ML] Detected: {intent.upper()} (confidence: {confidence*100:.1f}%)")
        
        # Log task
        self.task_history.append({
            'command': command,
            'intent': intent,
            'confidence': confidence,
            'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Execute task
        return self.execute_task(intent, command)
    
    def execute_task(self, intent, command):
        """Execute the appropriate task based on intent"""
        
        if intent == "time":
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.respond(f"The current time is {current_time}")
        
        elif intent == "date":
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            day = datetime.datetime.now().strftime("%A")
            self.respond(f"Today is {day}, {current_date}")
        
        elif intent == "search":
            query = command.replace("search for", "").replace("search", "")
            query = query.replace("google", "").replace("look up", "")
            query = query.replace("find information about", "").strip()
            
            if query:
                self.respond(f"Searching for: {query}")
                print(f"[ACTION] Opening browser...")
                # In real implementation: webbrowser.open(f"https://google.com/search?q={query}")
            else:
                self.respond("What would you like me to search for?")
        
        elif intent == "greeting":
            hour = datetime.datetime.now().hour
            if hour < 12:
                greeting = "Good morning"
            elif hour < 18:
                greeting = "Good afternoon"
            else:
                greeting = "Good evening"
            self.respond(f"{greeting}! How can I assist you?")
        
        elif intent == "farewell":
            self.respond("Goodbye! Have a great day!")
            return False  # Exit
        
        elif intent == "help":
            self.show_help()
        
        elif intent == "joke":
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "What's a machine learning expert's favorite type of music? Heavy Metal Learning!",
                "Why did the neural network go to therapy? It had too many hidden layers!",
                "How many data scientists does it take to change a light bulb? Just one, but they'll need 10,000 examples first!",
            ]
            self.respond(random.choice(jokes))
        
        elif intent == "calculate":
            self.calculate(command)
        
        elif intent == "weather":
            self.respond("I would need a weather API to check real-time weather. "
                        "In a full implementation, I'd connect to OpenWeatherMap or similar service.")
        
        else:
            self.respond("I'm not sure how to handle that. Try asking for help!")
        
        return True
    
    def calculate(self, command):
        """Perform calculations"""
        try:
            # Replace words with operators
            expr = command.replace("plus", "+").replace("add", "+")
            expr = expr.replace("minus", "-").replace("subtract", "-")
            expr = expr.replace("times", "*").replace("multiply", "*")
            expr = expr.replace("divided by", "/").replace("divide", "/")
            
            # Extract only numbers and operators
            expr = re.sub(r'[^0-9+\-*/().]', ' ', expr)
            expr = ' '.join(expr.split())
            
            if expr:
                result = eval(expr)
                self.respond(f"The answer is {result}")
            else:
                self.respond("I couldn't understand the calculation")
        
        except Exception as e:
            self.respond("Sorry, I couldn't perform that calculation")
    
    def show_help(self):
        """Display available commands"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                         ║
╠══════════════════════════════════════════════════════════════╣
║  ⏰ Time & Date                                               ║
║     • "what time is it"                                       ║
║     • "what's the date today"                                 ║
║                                                               ║
║  🔍 Web Search                                                ║
║     • "search for [topic]"                                    ║
║     • "google [topic]"                                        ║
║                                                               ║
║  🧮 Calculations                                              ║
║     • "calculate 5 plus 3"                                    ║
║     • "what is 10 times 2"                                    ║
║                                                               ║
║  😄 Fun                                                       ║
║     • "tell me a joke"                                        ║
║                                                               ║
║  👋 Interaction                                               ║
║     • "hello" / "hi"                                          ║
║     • "goodbye" / "exit"                                      ║
║     • "help" / "what can you do"                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(help_text)
    
    def show_statistics(self):
        """Show usage statistics"""
        if not self.task_history:
            print("\n[STATS] No tasks executed yet")
            return
        
        print("\n" + "="*70)
        print("SESSION STATISTICS")
        print("="*70)
        
        # Count intents
        intent_counts = {}
        for task in self.task_history:
            intent = task['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        print(f"\nTotal commands: {len(self.task_history)}")
        print("\nIntent distribution:")
        for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * count
            print(f"  {intent:12} : {bar} ({count})")
        
        # Average confidence
        avg_conf = sum(t['confidence'] for t in self.task_history) / len(self.task_history)
        print(f"\nAverage confidence: {avg_conf*100:.1f}%")
    
    def run(self):
        """Main interaction loop"""
        print("\n" + "="*70)
        print("ASSISTANT READY - Type your commands")
        print("Type 'exit' or 'quit' to stop | Type 'help' for commands")
        print("="*70)
        
        while True:
            try:
                # Get user input
                command = input("\nYou: ").strip()
                
                if not command:
                    continue
                
                # Process command
                continue_running = self.process_command(command)
                
                if not continue_running:
                    break
            
            except KeyboardInterrupt:
                print("\n\n[INTERRUPTED] Shutting down...")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")
        
        # Show statistics
        self.show_statistics()
        
        print("\n" + "="*70)
        print("SESSION ENDED")
        print("="*70)


def demo():
    """
    Run automated demo showing all features
    """
    print("\n" + "="*70)
    print("DEMO MODE - Automated Feature Showcase")
    print("="*70)
    
    assistant = SimpleVirtualAssistant(name="Demo Bot")
    
    demo_commands = [
        "hello",
        "what time is it",
        "what's the date today",
        "calculate 25 plus 17",
        "tell me a joke",
        "search for machine learning",
        "help",
        "goodbye"
    ]
    
    print("\n" + "="*70)
    print("RUNNING DEMO COMMANDS")
    print("="*70)
    
    for i, cmd in enumerate(demo_commands, 1):
        print(f"\n{'─'*70}")
        print(f"Demo {i}/{len(demo_commands)}")
        input(f"Press ENTER to execute: '{cmd}'")
        assistant.process_command(cmd)
    
    assistant.show_statistics()


def test_intent_classifier():
    """
    Test the intent classification with various commands
    """
    print("\n" + "="*70)
    print("INTENT CLASSIFIER TEST")
    print("="*70)
    
    assistant = SimpleVirtualAssistant(name="Test Bot")
    
    test_commands = [
        "what's the current time",
        "tell me today's date",
        "find information about python",
        "good morning",
        "compute 10 plus 5",
        "tell me something funny",
        "I need help",
        "see you later"
    ]
    
    print("\n" + "="*70)
    print("Testing Intent Classification")
    print("="*70)
    
    print(f"\n{'Command':<40} {'Intent':<15} {'Confidence'}")
    print("─"*70)
    
    for cmd in test_commands:
        intent, confidence = assistant.predict_intent(cmd)
        print(f"{cmd:<40} {intent:<15} {confidence*100:.1f}%")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VIRTUAL ASSISTANT - TEXT DEMO")
    print("="*70)
    print("\nChoose mode:")
    print("  1. Interactive Mode (chat with assistant)")
    print("  2. Demo Mode (automated showcase)")
    print("  3. Test Mode (test intent classifier)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        assistant = SimpleVirtualAssistant(name="Assistant")
        assistant.run()
    elif choice == "2":
        demo()
    elif choice == "3":
        test_intent_classifier()
    else:
        print("Invalid choice. Starting interactive mode...")
        assistant = SimpleVirtualAssistant(name="Assistant")
        assistant.run()