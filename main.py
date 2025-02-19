# Dont Forgot To give Respect To Me If you use It 
from Frontend.GUI import (GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen, TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, QueryModifier, GetAssistantStatus, GetMicrophoneStatus)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.TextToSpeech import TextToSpeech
from Backend.Chatbot import ChatBot
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os


# Use all Api keys and other important key's from .env file for safety reason 

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname} , How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocess = []
Functions = ["open", "close" , "play", "system", "content", "google search" , "youtube search"]

def ShowfaultChatNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as db_file:
                db_file.write(DefaultMessage)
            
def ReadChatLogJson():
    with open(r'Data\ChatLog.json','r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
        return chatlog_data
    
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User : {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant : {entry['content']}\n"
            
    formatted_chatlog = formatted_chatlog.replace("User",Username +" ") 
    formatted_chatlog = formatted_chatlog.replace("User",Username +" ")
    
    with open(TempDirectoryPath('Database.data'),'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))     
        
def ShowChatOnGUI():
    with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
        data = file.read()
    if len(str(data)) > 0:
        lines = data.split('\n')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Response.data'), 'w', encoding='utf-8') as file:
            file.write(result)
        
def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen(" ")
    ShowfaultChatNoChats()
    ChatLogIntegration()
    
InitialExecution()
# Dont Forgot To give Respect To Me If you use It 
import subprocess
import os

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = " "
    
    subprocesses = []
    
    SetAssistantStatus("Listening....")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking....")
    
    Decision = [d.lower() for d in FirstLayerDMM(Query)]
    print(" ")
    print(f"Decision : {Decision}")
    print(" ")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        {" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")}
    )
    
    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True
    
    if not TaskExecution:
        for queries in Decision:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True
                break
            
    if ImageExecution:
        os.makedirs(r'Frontend\Files', exist_ok=True)
        
        with open(r'Frontend\Files\ImageGeneration.data', 'w', encoding='utf-8') as file:
            file.write(f"{ImageGenerationQuery},True")

        try:
            proc = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(proc) 
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching.....")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering....")
        TextToSpeech(Answer)      
        return True 

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking....")
                QueryFinal = Query.replace("general", "")  
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            elif "Who Made you" in Queries or "Who is Your Creator" in Query or "Who is your Boss" in Query or "Who is Boss" in Query or "Who Named you" in Query or "Who Gave you mind" in Query:
                SetAssistantStatus("Thinking....")
                QueryFinal = "Sir You set me in this Desktop But My Boss always is Arya !" 
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True
            
            elif "realtime" in Queries:
                SetAssistantStatus("Searching....")
                QueryFinal = Query.replace("realtime", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True    

            elif "exit" in Queries:
                QueryFinal = "Okay Boss , Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer) 
                SetAssistantStatus("Answering....")
                os._exit(1)  
                             
def FirstThread():
    TextToSpeech("Hello Sir I am Supriya Arya's Assistant , How I help you today")
    while True:
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()
                
        else:
            AIStatus = GetAssistantStatus()
            if "Avialable..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available....")    
                            
# Dont Forgot To give Respect To Me If you use It 
                
def SecondThread():
    GraphicalUserInterface()
    
if __name__ == "__main__":
    thread2  = threading.Thread(target=FirstThread , daemon=True)
    thread2.start()
    SecondThread()    
                          
                         
                               
 
            
               
                   
                   
