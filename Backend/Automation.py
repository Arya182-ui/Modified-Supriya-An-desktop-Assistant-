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
import platform
import datetime
import pyperclip
import cv2
from PIL import ImageGrab
from screen_brightness_control import set_brightness
from Backend.security import SecuritySystem  
from Backend.TaskManager import task_manager, create_task_voice, list_tasks_voice, complete_task_voice
from Backend.EmailManager import email_manager, read_emails_voice, send_email_voice, email_summary_voice
from Backend.FileManager import file_manager, list_files_voice, search_files_voice, organize_files_voice
from Backend.SystemMonitor import system_monitor, get_system_status_voice, get_top_processes_voice, get_network_status_voice
from Backend.MediaController import media_controller, play_music_voice, volume_control_voice, record_audio_voice, library_stats_voice


env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
security = SecuritySystem()
OS_NAME = platform.system()


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
    if "mute" in command:
        keyboard.press_and_release("volume mute")
    elif "volume up" in command:
        keyboard.press_and_release("volume up")
    elif "volume down" in command:
        keyboard.press_and_release("volume down")
    elif "brightness" in command:
        try:
            level = int(command.split()[-1])
            set_brightness(level)
            print(f"✅ Brightness set to {level}%")
        except:
            print("❌ Invalid brightness level.")
    elif "shutdown" in command:
        if security.requires_auth("shutdown") and not security.authenticate():
            print("🔐 Shutdown blocked.")
            return
        security.log_action("System Shutdown")
        if OS_NAME == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown now")
    elif "reboot" in command:
        if security.requires_auth("reboot") and not security.authenticate():
            print("🔐 Reboot blocked.")
            return
        security.log_action("System Reboot")
        if OS_NAME == "Windows":
            os.system("shutdown /r /t 1")
        else:
            os.system("reboot")

def Screenshot():
    filename = f"Data/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    ImageGrab.grab().save(filename)
    print(f"📸 Screenshot saved: {filename}")

def WebcamCapture():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    filename = f"Data/webcam_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    if ret:
        cv2.imwrite(filename, frame)
        print(f"📸 Webcam image saved: {filename}")
    cam.release()
    cv2.destroyAllWindows()

def ClipboardControl(action, data=""):
    if action == "copy":
        pyperclip.copy(data)
        print("📋 Copied to clipboard.")
    elif action == "paste":
        print("📋 Clipboard content:", pyperclip.paste())


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.strip().lower()

        if command.startswith("open"):
            app = command.replace("open", "").strip()
            fun = asyncio.to_thread(OpenApp, app)
            funcs.append(fun)

        elif command.startswith("close"):
            app = command.replace("close", "").strip()
            fun = asyncio.to_thread(CloseApp, app)
            funcs.append(fun)

        elif command.startswith("system"):
            fun = asyncio.to_thread(System, command.replace("system", "").strip())
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
            
        elif command.startswith("clipboard copy"):
            text = command.replace("clipboard copy", "").strip()
            fun = asyncio.to_thread(ClipboardControl, "copy", text)
            funcs.append(fun)

        elif command.startswith("clipboard paste"):
            fun = asyncio.to_thread(ClipboardControl, "paste")
            funcs.append(fun)

        elif command == "screenshot":
            fun = asyncio.to_thread(Screenshot)
            funcs.append(fun)

        elif command == "webcam":
            fun = asyncio.to_thread(WebcamCapture)
            funcs.append(fun)
            
        # New super features
        elif command.startswith("task"):
            task_command = command.replace("task", "").strip()
            if "create" in task_command:
                result = create_task_voice(command)
            elif "list" in task_command or "show" in task_command:
                result = list_tasks_voice(command)
            elif "complete" in task_command or "done" in task_command:
                result = complete_task_voice(command)
            else:
                result = list_tasks_voice(command)
            print(f"📋 Task: {result}")
            
        elif command.startswith("email"):
            email_command = command.replace("email", "").strip()
            if "read" in email_command or "check" in email_command:
                result = read_emails_voice(command)
            elif "send" in email_command:
                result = send_email_voice(command)
            elif "summary" in email_command or "stats" in email_command:
                result = email_summary_voice(command)
            else:
                result = read_emails_voice(command)
            print(f"📧 Email: {result}")
            
        elif command.startswith("file"):
            file_command = command.replace("file", "").strip()
            if "list" in file_command or "show" in file_command:
                result = list_files_voice(command)
            elif "search" in file_command or "find" in file_command:
                result = search_files_voice(command)
            elif "organize" in file_command:
                result = organize_files_voice(command)
            else:
                result = list_files_voice(command)
            print(f"📁 File: {result}")
            
        elif command.startswith("monitor"):
            monitor_command = command.replace("monitor", "").strip()
            if "status" in monitor_command or "system" in monitor_command:
                result = get_system_status_voice(command)
            elif "process" in monitor_command:
                result = get_top_processes_voice(command)
            elif "network" in monitor_command:
                result = get_network_status_voice(command)
            else:
                result = get_system_status_voice(command)
            print(f"📊 Monitor: {result}")
            
        elif command.startswith("media"):
            media_command = command.replace("media", "").strip()
            if "play" in media_command or "music" in media_command:
                result = play_music_voice(command)
            elif "volume" in media_command:
                result = volume_control_voice(command)
            elif "record" in media_command:
                result = record_audio_voice(command)
            elif "stats" in media_command or "library" in media_command:
                result = library_stats_voice(command)
            else:
                result = play_music_voice(command)
            print(f"🎵 Media: {result}")
            
        elif command.startswith("record"):
            result = record_audio_voice(command)
            print(f"🎤 Record: {result}")
            
        elif command.startswith("organize"):
            result = organize_files_voice(command)
            print(f"🗂️ Organize: {result}")
            
        elif command.startswith("search files"):
            result = search_files_voice(command)
            print(f"🔍 Search: {result}")

        else:
            print(f"❓ Unknown command: {command}")

    await asyncio.gather(*funcs)


async def Automation(commands: list[str]):
    await TranslateAndExecute(commands)
    return True
