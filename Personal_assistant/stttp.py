import streamlit as st
import speech_recognition as sr
import requests
import datetime
import pyttsx3
import wikipedia

# Streamlit Page Configuration
st.set_page_config(page_title="Voice-Activated Personal Assistant", layout="centered")
st.title("🗣️ Voice-Activated Personal Assistant")
st.write("This assistant can check the weather, provide the latest news, set alarms, and answer general questions.")

# Text-to-Speech (TTS) Function
def speak(text):
    """Speak function to avoid 'run loop already started' errors."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

# Session State Setup
if "command" not in st.session_state:
    st.session_state["command"] = ""

# Speech Recognizer
r = sr.Recognizer()

# Map of country names to NewsAPI country codes
country_code_map = {
    "india": "in",
    "united states": "us",
    "united kingdom": "gb",
    "australia": "au",
    "canada": "ca",
    "germany": "de",
    "france": "fr",
    "japan": "jp",
    "china": "cn",
    "asia": ""  # Blank because "everything" endpoint doesn't use country codes for broad searches
}

# Function to parse news query
def parse_news_query(query):
    """Parses the user's news query and returns the category and country."""
    category = "general"
    country = "in"  # Default to India

    # Extract category from query
    for cat in ["sports", "technology", "business", "entertainment", "science", "health"]:
        if cat in query:
            category = cat
            break

    # Extract country from query
    for c in country_code_map.keys():
        if c in query:
            country = c
            break

    return category, country

# Fetch News Function
def fetch_news(query):
    """Fetches news based on parsed category and country."""
    category, country = parse_news_query(query)
    country_code = country_code_map.get(country, "")  # Blank if country doesn't use country code
    
    # Use "top-headlines" if country is available, else fallback to "everything"
    if country_code:
        url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={category}&apiKey=280df3ee883d47aa9b625237c18c2cb4"
    else:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey=280df3ee883d47aa9b625237c18c2cb4"

    response = requests.get(url).json()

    if response.get("status") == "ok" and response.get("articles"):
        articles = response["articles"][:5]
        news_headlines = f"Here are the top {category} headlines in {country.capitalize()}:" if country_code else f"Here are the top results for '{query}':"

        for i, article in enumerate(articles, start=1):
            headline = article.get("title", "No title available")
            st.write(f"{i}. **{headline}**")
            st.write(f"Source: {article.get('source', {}).get('name', 'Unknown')}")
            st.write(f"[Read more]({article.get('url', '#')})")
            st.write("---")
            news_headlines += f" Headline {i}: {headline}. "

        speak(news_headlines)
    else:
        error_message = f"Unable to fetch news for '{query}'. Please try again later."
        st.write(error_message)
        speak(error_message)

# Fetch Weather Function
def fetch_weather(city):
    api_key = "13b796249eb4707684ea7de952b1aea0"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") == 200:
        weather_info = f"Weather in {city}: {response['main']['temp']}°C, {response['weather'][0]['description']}."
        st.write(f"🌤️ {weather_info}")
        speak(weather_info)
    else:
        error_message = f"Could not find weather information for {city}. Please check the city name."
        st.write(error_message)
        speak(error_message)

# Set Alarm
def set_alarm(alarm_time):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    st.write(f"⏰ Alarm set for {alarm_time}. Current time: {current_time}.")
    speak(f"Alarm set for {alarm_time}. Current time is {current_time}.")

# Handle General Wikipedia Queries
def handle_general_query(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        st.write(f"📚 {summary}")
        speak(summary)
    except Exception:
        st.write("Sorry, I couldn't find relevant information.")
        speak("Sorry, I couldn't find an answer for that.")

# Main Function to Listen and Process Voice Commands
def listen_and_execute_command():
    st.session_state["command"] = ""
    with sr.Microphone() as source:
        st.write("Listening for your command... (Ensure microphone access is enabled)")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio).lower()
        st.write(f"Command Received: {command}")
        st.session_state["command"] = command

        if "news" in command:
            fetch_news(command)

        elif "weather" in command:
            if "weather in" in command:
                city = command.split("weather in")[-1].strip()
            else:
                city = "your city"
            fetch_weather(city)

        elif "set alarm" in command:
            alarm_time = command.split("set alarm for")[-1].strip()
            set_alarm(alarm_time)

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            st.write(f"🕒 Current Time: {current_time}")
            speak(f"The current time is {current_time}.")

        else:
            handle_general_query(command)

    except sr.UnknownValueError:
        st.write("Sorry, I could not understand your voice.")
        speak("Sorry, I could not understand your command.")
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition; {e}")
        speak("There was a problem connecting to the voice recognition service.")

# Button to Trigger Voice Command Listening
if st.button("🎤 Speak Now"):
    listen_and_execute_command()
