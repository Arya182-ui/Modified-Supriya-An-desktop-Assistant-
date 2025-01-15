# Dont Forgot To give Respect To Me(Arya) If you use It 
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from pywinauto.application import Application

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqeee", "tw-Data-text tw-text-small tw-ta",
    "IZ6rdc", "O5uR6d", "vlzY6d", "webanswers-webanswer_table_webanswer-table", "dDono ikb4Bb gsrt", "sXLaOe", "LWkfKe",
    "VQF4g", "qv3Wpe", "kmo-rdesc", "SPZz6b"
]

ugeragent = 'Mozila/5.0 (windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML , like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your Satisfaction is my top priority : feel free to reach out if there's anything else I can help you with."
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]

messages = []

SystemChatBot = [{"role":"system","content" : f"Hello, I am {os.environ['Username']}, You're a content writer. You have to Write content like letter, codes, applications, essay, notes, songs, poems etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def content(Topic):
    def OpenNotepad(File):
        default_text_edtior = "Notepad.exe"
        subprocess.Popen([default_text_edtior , File])
        
    def ContentWriterAI(prompt):
        messages = [{"role": "user", "content": f"{prompt}"}]
        
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=SystemChatBot + messages,
            max_tokens=2048,
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
        messages.append({"role": "assistant", "content": Answer})
        return Answer 
    
    Topic = Topic.replace("content", " ")
    ContentByAI = ContentWriterAI(Topic)
        
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")   
    return True

def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/result?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYouTube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):
    try:
        app = Application().start(app)  
        print(f"{app} launched successfully!")
        return True

    except Exception as e:
        print(f"Error opening app locally: {e}")
        
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            }
            try:
                response = sess.get(url, headers=headers)
                response.raise_for_status()  
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve search results: {e}")
                return None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webbrowser.open(links[0]) 
            else:
                print("No links found.")
        return True
    
def CloseApp(app_name):
    app_name = app_name.lower()
    result = os.popen(f'tasklist').read()
    if "chrome" in app_name.lower():
        pass
    else:
        if app_name in result.lower():
            os.system(f"taskkill /F /IM {app_name}.exe")
            print(f"{app_name} has been closed successfully!")
        else:
            print(f"The process {app_name} was not found.")
            
    return True
        
def System(command):
    def mute():
        keyboard.press_and_release("volume mute") 
        
    def volume_up():
        keyboard.press_and_release("volume up")
             
    def volume_down():
        keyboard.press_and_release("volume down")   
        
    if command == "mute" or "unmute":
        mute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()  
        
    return True      
                                   
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    
    for command in commands:
        if command.startswith("open"):
            if "open it" in command:
                pass
            
            if "open file" == command:
                pass
            
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open"))    
                funcs.append(fun)
                
        elif command.startswith("general"):
            pass
        
        elif command.startswith("realtime"):
            pass 
        
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close"))
            funcs.append(fun)
            
        elif command.startswith("play"):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play"))
            funcs.append(fun)

        elif command.startswith("content"):
            fun = asyncio.to_thread(content, command.removeprefix("content"))
            funcs.append(fun)
            
        elif command.startswith("google search"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search"))
            funcs.append(fun)

        elif command.startswith("youtube search"):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search"))
            funcs.append(fun)

        elif command.startswith("system"):
            fun = asyncio.to_thread(System, command.removeprefix("system"))
            funcs.append(fun)
            
        else:
            print(f"No Function found. For{command}")
            
    results = await asyncio.gather(*funcs) 
    
    for result in results:
        if isinstance(result , str):
            yield result
        else:
            yield result
            
async def Automation(commands:list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    
    return True  

            
            
                      
                                                                                                      
                                                                        
                                                                  
                    
        