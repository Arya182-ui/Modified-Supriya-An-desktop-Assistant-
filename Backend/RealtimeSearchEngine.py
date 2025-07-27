# Dont Forgot To give Respect To Me(Arya) If you use It 

from googlesearch import search
from groq import Groq
from json import load, dump
import os
import datetime
from dotenv import dotenv_values
import requests
import geocoder

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
WeatherAPIKey = env_vars.get("WeatherAPIKey")

if not (Username and Assistantname and GroqAPIKey):
    raise ValueError("Missing required environment variables in .env file.")

try:
    client = Groq(api_key=GroqAPIKey)
except Exception as e:
    raise ConnectionError(f"Failed to initialize Groq client: {e}")

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


SystemChatBot = [{"role": "system", "content": System}]

if not os.path.exists("Data"):
    os.makedirs("Data")

chat_log_path = r"Data\ChatLog.json"
if not os.path.exists(chat_log_path):
    with open(chat_log_path, "w") as f:
        dump([], f)
        
        
def GoogleSearch(query):
    result = list(search(query, advanced=True, num_results=5))
    Answer = f"The Search result for '{query}' are:\n[start]\n"
    
    for i in result:
        Answer += f"Title:{i.title}\nDescription: {i.description}\n\n"
        
    Answer +="[end]"
    return Answer

def AnswerModifier(Answer):
    """Clean up the chatbot's response."""
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

SystemChatBot=[
    {"role": "system","content": System},
    {"role": "user","content":"Hi"},
    {"role": "assistant","content":"Hello , how can i help you?"}
]

def get_gps_location():
    """
    Get the current location based on GPS (or IP fallback if GPS is unavailable).
    """
    g = geocoder.ip('me')  

    if g.latlng:
        latitude, longitude = g.latlng
        city = g.city
        region = g.state
        country = g.country
        return latitude, longitude, city, region, country
    else:
        
        return get_ipinfo_location()

def get_ipinfo_location():
    """
    Get the location information from IPinfo API in case GPS is unavailable.
    """
    ip_info_url = "http://ipinfo.io/json"
    try:
        response = requests.get(ip_info_url)
        location_data = response.json()
        loc = location_data.get("loc", "0,0")  
        latitude, longitude = loc.split(",")
        city = location_data.get("city", "Unknown City")
        region = location_data.get("region", "Unknown Region")
        country = location_data.get("country", "Unknown Country")

        return latitude, longitude, city, region, country
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP location: {e}")
        return None, None, "Unknown City", "Unknown Region", "Unknown Country"

def fetch_live_data():
    """
    Fetch live weather data using the user's GPS or IP-based location and OpenWeatherMap API.
    """
    latitude, longitude, city, region, country = get_gps_location()

    if latitude and longitude:
        api_key = WeatherAPIKey
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"  

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("weather"):
                weather_description = data["weather"][0]["description"]
                temperature = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                pressure = data["main"]["pressure"]
                wind_speed = data["wind"]["speed"]
                cloudiness = data["clouds"]["all"]

                weather_info = (
                    f"Location: {city}, {region}, {country}\n"
                    f"Weather: {weather_description}\n"
                    f"Temperature: {temperature}°C\n"
                    f"Humidity: {humidity}%\n"
                    f"Pressure: {pressure} hPa\n"
                    f"Wind Speed: {wind_speed} m/s\n"
                    f"Cloudiness: {cloudiness}%"
                )

                return weather_info
            else:
                return "Weather data not available."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return "Could not fetch weather data."
    else:
        return "Could not determine location."

def Information():
    current_date_time = datetime.datetime.now()
    
    day = current_date_time.strftime('%A')
    date = current_date_time.strftime('%d')
    month = current_date_time.strftime('%B')
    year = current_date_time.strftime('%Y')
    hour = current_date_time.strftime('%H')
    minute = current_date_time.strftime('%M')
    second = current_date_time.strftime('%S')

    weather = fetch_live_data()

    info = "Use the Real-time Information if needed:\n"
    info += f"Day : {day}\n"
    info += f"Date : {date}\n"
    info += f"Month : {month}\n"
    info += f"Year : {year}\n"
    info += f"Time : {hour} hours, {minute} minutes, {second} seconds.\n"
    info += f"Weather : {weather}\n"
    
    return info
    
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages 
    
    with open(r"Data\ChatLog.json","r") as f:
        message = load(f)
    message.append({"role":"user","content": f"{prompt}"})
    
    SystemChatBot.append({"role":"user","content":GoogleSearch(prompt)})
    
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + message,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None    
    )
        
    Answer = ""
        
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
                
    Answer = Answer.replace("</s>", "")  
        
    message.append({"role": "assistant", "content": Answer})
    
    with open(r"Data\ChatLog.json", "w") as f:
        dump(message, f, indent=4)
    SystemChatBot.pop()        
    return AnswerModifier(Answer=Answer)   

if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Question: ")
        print(RealtimeSearchEngine(prompt)) 
    
