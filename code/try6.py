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
            results = self.classifier(text, top_k=3)  # Get top 3 emotions
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
                # Clean up the topic
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
        # This is a placeholder - in a real implementation you would use the YouTube API
        return f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def listen(self