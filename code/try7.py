from transformers import pipeline
import re
import requests
import speech_recognition as sr
from datetime import datetime
from colorama import Fore, Style, init
import time

# Initialize colorama
init()

class EmotionAnalyzer:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion")
    
    def detect(self, text):
        try:
            results = self.classifier(text, top_k=3)
            return [{"label": r['label'].lower(), "score": round(r['score'], 2)} for r in results]
        except Exception as e:
            print(f"{Fore.RED}Emotion detection error: {e}{Style.RESET_ALL}")
            return []

class StudyHelper:
    def __init__(self):
        self.formulas = {
            "velocity": "v = d / t",
            "force": "F = m * a",
            "energy": "E = mc²",
            "quadratic": "x = (-b ± √(b² - 4ac)) / 2a",
            "speed": "v = d / t",
            "ohm's law": "V = IR",
            "pythagoras theorem": "a² + b² = c²",
            "area of circle": "A = πr²",
            "kinetic energy": "KE = ½mv²"
        }
        self.keywords = ["learn about", "study", "understand", "explore", "revise", "interested in", "topic is", "teach me", "explain"]
    
    def find_topic(self, text):
        text = text.lower()
        for key in self.keywords:
            if key in text:
                part = text.split(key)[-1].strip()
                part = re.sub(r'[^a-zA-Z0-9 ]', '', part)
                return part.capitalize()
        
        if len(text.split()) <= 5:
            return text.capitalize()
        return None
    
    def get_formula(self, topic):
        topic = topic.lower()
        for key in self.formulas:
            if key in topic:
                return self.formulas[key]
        return None
    
    def get_wiki_summary(self, topic):
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("extract", "No summary available.")
        except requests.exceptions.RequestException as e:
            return f"Could not fetch information: {str(e)}"
    
    def get_youtube_link(self, topic):
        return f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def listen(self):
        with sr.Microphone() as source:
            print(f"{Fore.CYAN}\nListening... (speak now){Style.RESET_ALL}")
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print(f"{Fore.CYAN}Processing your speech...{Style.RESET_ALL}")
                text = self.recognizer.recognize_google(audio)
                print(f"{Fore.GREEN}You said: {text}{Style.RESET_ALL}")
                return text
            except sr.WaitTimeoutError:
                print(f"{Fore.YELLOW}No speech detected.{Style.RESET_ALL}")
                return ""
            except sr.UnknownValueError:
                print(f"{Fore.RED}Sorry, could not understand your speech.{Style.RESET_ALL}")
                return ""
            except sr.RequestError:
                print(f"{Fore.RED}Speech recognition service unavailable.{Style.RESET_ALL}")
                return ""

class StudyAssistant:
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.study_helper = StudyHelper()
        self.speech_recognizer = SpeechRecognizer()
        self.user_profile = {"name": "", "study_sessions": []}
        self.setup_profile()
    
    def setup_profile(self):
        print(f"\n{Fore.MAGENTA}=== Study Assistant Setup ===")
        self.user_profile["name"] = input(f"{Style.RESET_ALL}What's your name? ").strip() or "Student"
        print(f"{Fore.GREEN}Welcome, {self.user_profile['name']}!{Style.RESET_ALL}")
    
    def get_motivation(self, emotions):
        messages = {
            "joy": "You're feeling joyful! Keep the positivity going!",
            "sadness": "Feeling sad is okay. Start with something small and keep going.",
            "anger": "Try taking a deep breath. Calm helps you focus better.",
            "fear": "Don't worry — learning step-by-step makes things easier.",
            "love": "That's a great mindset. Use your energy to do something meaningful!",
            "surprise": "Interesting! Let's explore the topic together.",
            "neutral": "Let's focus and make progress!"
        }
        
        if not emotions:
            return messages["neutral"]
        
        primary_emotion = emotions[0]['label']
        color = {
            "joy": Fore.YELLOW,
            "sadness": Fore.BLUE,
            "anger": Fore.RED,
            "fear": Fore.MAGENTA,
            "love": Fore.LIGHTMAGENTA_EX,
            "surprise": Fore.CYAN
        }.get(primary_emotion, Fore.WHITE)
        
        return f"{color}{messages.get(primary_emotion, messages['neutral'])}{Style.RESET_ALL}"
    
    def track_study_session(self, topic, duration):
        self.user_profile["study_sessions"].append({
            "topic": topic,
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def show_study_progress(self):
        if not self.user_profile["study_sessions"]:
            print(f"{Fore.YELLOW}No study sessions recorded yet.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.MAGENTA}=== Your Study Progress ===")
        total_time = sum(s['duration'] for s in self.user_profile["study_sessions"])
        print(f"{Fore.CYAN}Total study time: {total_time} seconds{Style.RESET_ALL}")
        
        topics = {}
        for session in self.user_profile["study_sessions"]:
            topics[session['topic']] = topics.get(session['topic'], 0) + session['duration']
        
        print(f"\n{Fore.BLUE}Topics you've studied:{Style.RESET_ALL}")
        for topic, duration in topics.items():
            print(f"- {topic}: {duration} seconds")
        
        if len(self.user_profile["study_sessions"]) > 1:
            dates = [datetime.strptime(s['timestamp'], "%Y-%m-%d %H:%M:%S").date() 
                    for s in self.user_profile["study_sessions"]]
            unique_days = len(set(dates))
            print(f"\n{Fore.GREEN}Study streak: {unique_days} day(s){Style.RESET_ALL}")

    def show_help_menu(self):
        print(f"\n{Fore.MAGENTA}=== Help Menu ===")
        print(f"{Fore.CYAN}Available commands:{Style.RESET_ALL}")
        print("- 'progress': Show your study progress")
        print("- 'formulas': List all available formulas")
        print("- 'exit': Quit the program")
        print("- 'help': Show this menu")
        print(f"\n{Fore.BLUE}You can also:{Style.RESET_ALL}")
        print("- Share your feelings (I'm feeling anxious about...)")
        print("- Ask to study a topic (I want to learn about velocity)")
        print("- Request formulas (What's the formula for force?)")

    def list_formulas(self):
        print(f"\n{Fore.MAGENTA}=== Available Formulas ===")
        for topic, formula in self.study_helper.formulas.items():
            print(f"{Fore.CYAN}{topic.capitalize():<20}: {Fore.GREEN}{formula}{Style.RESET_ALL}")

    def get_input(self):
        choice = input(f"\n{Fore.CYAN}Press '1' to type or '2' to speak (or 'exit' to quit): {Style.RESET_ALL}").strip()
        
        if choice.lower() == 'exit':
            return None
        
        if choice == '2':
            return self.speech_recognizer.listen()
        else:
            return input(f"{Fore.CYAN}Tell me how you're feeling or what you want to study: {Style.RESET_ALL}")

    def handle_special_commands(self, user_input):
        user_input = user_input.lower().strip()
        
        if user_input == 'progress':
            self.show_study_progress()
            return True
        elif user_input == 'formulas':
            self.list_formulas()
            return True
        elif user_input == 'help':
            self.show_help_menu()
            return True
        return False

    def show_progress_report(self):
        if not self.user_profile["study_sessions"]:
            print(f"\n{Fore.YELLOW}No study sessions were recorded.{Style.RESET_ALL}")
        else:
            total_time = sum(s['duration'] for s in self.user_profile["study_sessions"])
            unique_topics = len(set(s['topic'] for s in self.user_profile["study_sessions"]))
            
            print(f"\n{Fore.MAGENTA}=== Your Study Summary ===")
            print(f"{Fore.CYAN}Total study time: {total_time} seconds")
            print(f"Topics covered: {unique_topics}")
            
            avg_time = total_time / len(self.user_profile["study_sessions"])
            print(f"Average session: {avg_time:.2f} seconds{Style.RESET_ALL}")
            
            topic_counts = {}
            for session in self.user_profile["study_sessions"]:
                topic_counts[session['topic']] = topic_counts.get(session['topic'], 0) + 1
            
            if topic_counts:
                favorite_topic = max(topic_counts.items(), key=lambda x: x[1])
                print(f"\n{Fore.GREEN}Your most studied topic: {favorite_topic[0]} ({favorite_topic[1]} sessions){Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Goodbye, {self.user_profile['name']}! Keep up the good work!{Style.RESET_ALL}")

    def run(self):
        print(f"\n{Fore.MAGENTA}=== Study Assistant ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Hi {self.user_profile['name']}! I'm here to help you study.{Style.RESET_ALL}")
        self.show_help_menu()
        
        while True:
            user_input = self.get_input()
            
            if user_input is None:
                break
            
            if not user_input.strip():
                print(f"{Fore.YELLOW}No input detected. Please try again.{Style.RESET_ALL}")
                continue
            
            if self.handle_special_commands(user_input):
                continue
            
            start_time = time.time()
            
            emotions = self.emotion_analyzer.detect(user_input)
            if emotions:
                print(f"\n{Fore.MAGENTA}Emotion Analysis:{Style.RESET_ALL}")
                for emotion in emotions:
                    print(f"- {emotion['label'].capitalize()}: {emotion['score']}")
                print(f"\n{self.get_motivation(emotions)}")
            
            topic = self.study_helper.find_topic(user_input)
            if topic:
                print(f"\n{Fore.MAGENTA}Study Topic:{Style.RESET_ALL} {Fore.GREEN}{topic}{Style.RESET_ALL}")
                
                formula = self.study_helper.get_formula(topic)
                if formula:
                    print(f"{Fore.BLUE}Relevant Formula:{Style.RESET_ALL} {formula}")
                
                print(f"\n{Fore.CYAN}Fetching information...{Style.RESET_ALL}")
                notes = self.study_helper.get_wiki_summary(topic)
                youtube_link = self.study_helper.get_youtube_link(topic)
                
                print(f"\n{Fore.MAGENTA}Study Notes:{Style.RESET_ALL}\n{notes}")
                print(f"\n{Fore.BLUE}YouTube Resources:{Style.RESET_ALL} {youtube_link}")
                
                duration = round(time.time() - start_time, 2)
                self.track_study_session(topic, duration)
                print(f"\n{Fore.GREEN}Study session recorded: {duration} seconds{Style.RESET_ALL}")
            else:
                if not emotions:
                    print(f"\n{Fore.YELLOW}Couldn't detect a study topic or emotion. Try 'help' for options.{Style.RESET_ALL}")
            
            if self.user_profile["study_sessions"]:
                last_session = self.user_profile["study_sessions"][-1]
                print(f"\n{Fore.CYAN}Last study session: {last_session['topic']} ({last_session['duration']}s){Style.RESET_ALL}")
            
            print(f"\n{Fore.MAGENTA}=== Session Complete ==={Style.RESET_ALL}")
        
        self.show_progress_report()

if __name__ == "__main__":
    try:
        assistant = StudyAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Program interrupted. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")