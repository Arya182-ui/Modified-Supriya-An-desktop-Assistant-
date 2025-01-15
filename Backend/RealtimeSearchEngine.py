# Dont Forgot To give Respect To Me(Arya) If you use It 

from googlesearch import search
from groq import Groq
from json import load, dump
import os
import datetime
from dotenv import dotenv_values


env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

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

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime('%A')
    date = current_date_time.strftime('%d')
    month = current_date_time.strftime('%B')
    year = current_date_time.strftime('%Y')
    hour = current_date_time.strftime('%H') 
    minute = current_date_time.strftime('%M')
    second = current_date_time.strftime('%S')
    date += f"Use the Real-time Information if needed:\n"
    date += f"Day : {day}\n"
    date += f"Date : {date}\n"
    date += f"Month : {month}\n"
    date += f"Year : { year}\n"
    date += f"Time : {hour} hours , {minute} minute , {second} second.\n"
    return date
    
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
    