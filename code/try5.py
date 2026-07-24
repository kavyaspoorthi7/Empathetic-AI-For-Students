from transformers import pipeline
import re
import requests
import speech_recognition as sr

# Load emotion classifier model
emotion_classifier = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion")

# Detect emotion from text input
def detect_emotion(text):
    try:
        result = emotion_classifier(text)
        top_emotion = result[0]['label'].lower()
        return top_emotion
    except:
        return "none"

# Give motivational message based on emotion
def get_motivation(emotion):
    messages = {
        "joy": "You're feeling joyful! Keep the positivity going!",
        "sadness": "Feeling sad is okay. Start with something small and keep going.",
        "anger": "Try taking a deep breath. Calm helps you focus better.",
        "fear": "Don’t worry — learning step-by-step makes things easier.",
        "love": "That's a great mindset. Use your energy to do something meaningful!",
        "surprise": "Interesting! Let’s explore the topic together."
    }
    return messages.get(emotion, "You can do this!")

# Try to find a study topic from the input
def find_study_topic(text):
    keywords = ["learn about", "study", "understand", "explore", "revise", "interested in", "topic is"]
    for key in keywords:
        if key in text:
            part = text.split(key)[-1].strip()
            return part
    if len(text.split()) <= 5:
        return text
    return None

# Check if the topic has a known formula
def get_formula(topic):
    formulas = {
        "velocity": "v = d / t",
        "force": "F = m * a",
        "energy": "E = mc^2",
        "quadratic": "x = (-b ± √(b² - 4ac)) / 2a",
        "speed": "v = d / t",
        "ohm's law": "V = IR",
        "pythagoras theorem": "a² + b² = c²"
    }
    topic = topic.lower()
    for key in formulas:
        if key in topic:
            return formulas[key]
    return None

# Get study notes from Wikipedia
def get_study_notes(topic):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
    try:
        response = requests.get(url)
        data = response.json()
        if "extract" in data:
            return data["extract"]
        else:
            return "Sorry, no notes found."
    except:
        return "Something went wrong while fetching notes."

# Get input from microphone using speech recognition
def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak now.")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Processing your speech...")
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.WaitTimeoutError:
            print("No speech detected. Try again.")
            return ""
        except sr.UnknownValueError:
            print("Sorry, could not understand your speech.")
            return ""
        except sr.RequestError:
            print("Speech recognition service is not available.")
            return ""

# Main program logic
def run_assistant():
    print("Welcome to the Study Assistant!\n")
    choice = input("Press '1' to type or '2' to speak: ")

    if choice == '2':
        user_input = get_speech_input()
        if not user_input:
            return
    else:
        user_input = input("Tell me how you're feeling or what you want to study: ")

    if not user_input.strip():
        print("No input provided. Please try again.")
        return

    # Detect emotion
    emotion = detect_emotion(user_input)
    if emotion != "none":
        print("\nMotivational Message:", get_motivation(emotion))

    # Check for study topic
    topic = find_study_topic(user_input)
    if topic:
        print("\nStudy Topic:", topic)
        formula = get_formula(topic)
        if formula:
            print("Formula:", formula)
        print("\nFetching notes...")
        notes = get_study_notes(topic)
        print("\nNotes:\n", notes)
    else:
        # If no study topic, only show emotion if detected
        if emotion != "none":
            print("\nNo study topic detected. Only emotion was analyzed.")
        else:
            print("\nCouldn't find a clear study topic or emotion. Try rephrasing.")

# Run the assistant
# Loop the assistant until the user decides to exit
while True:
    run_assistant()
    print("\nType or say 'exit' to close the assistant, or press Enter to continue.")
    user_decision = input(">> ").strip().lower()
    if user_decision == "exit":
        print("Goodbye! Stay motivated and keep learning!")
        break
