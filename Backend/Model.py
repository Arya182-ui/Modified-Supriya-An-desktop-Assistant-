import cohere
from rich import print
from dotenv import dotenv_values
import random
import time


env_vars = dotenv_values(".env")
CohereAPIkey = env_vars.get("CohereAPIkey")

if not CohereAPIkey:
    print("[bold red]Error: CohereAPIkey is missing. Check your .env file.[/bold red]")
    exit(1)

co = cohere.Client(api_key=CohereAPIkey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", "task", "email", "file",
    "monitor", "media", "record", "organize", "search files",
    "backup", "security", "network", "schedule", "note"
]

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome , general open tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome , open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that I have a dancing performance on"},
    {"role": "Chatbot", "message": "general what is today's date , reminder 11:00 pm 6 jan dancing performance"},
]

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'task (task action and details)' if a query is about task management like 'create task buy groceries', 'mark task as complete', 'show my tasks', 'create task with high priority', etc.
-> Respond with 'email (email action and details)' if a query is about email management like 'read my emails', 'send email to john', 'check unread emails', 'compose email', etc.
-> Respond with 'file (file operation and details)' if a query is about file management like 'list files in downloads', 'search for document', 'organize my files', 'delete file', 'copy file', 'move file', etc.
-> Respond with 'monitor (system monitoring request)' if a query is about system monitoring like 'check system status', 'show cpu usage', 'monitor performance', 'show running processes', 'check memory usage', etc.
-> Respond with 'media (media control action)' if a query is about media control like 'play music', 'pause song', 'next track', 'volume up', 'start recording', 'stop music', etc.
-> Respond with 'record (recording type and details)' if a query is specifically about recording like 'record audio', 'start video recording', 'stop recording', 'record voice memo', etc.
-> Respond with 'organize (organization request)' if a query is about organizing files or data like 'organize downloads folder', 'sort files by type', 'clean up desktop', etc.
-> Respond with 'search files (search query)' if a query is specifically about searching files like 'find document about budget', 'search for photos from last month', etc.
-> Respond with 'backup (backup request)' if a query is about backing up data like 'backup my files', 'create backup', 'restore backup', etc.
-> Respond with 'security (security action)' if a query is about security like 'check security logs', 'change password', 'encrypt file', 'scan for threats', etc.
-> Respond with 'network (network action)' if a query is about network operations like 'check internet connection', 'show network status', 'test connectivity', etc.
-> Respond with 'schedule (scheduling action)' if a query is about scheduling like 'schedule meeting', 'add to calendar', 'set appointment', etc.
-> Respond with 'note (note action)' if a query is about taking notes like 'take note', 'save this information', 'create note', etc.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'system volume up' if the query is asking to increase volume like 'volume up', 'increase volume', etc.
-> Respond with 'system volume down' if the query is asking to decrease volume like 'volume down', 'lower the volume', etc.
-> Respond with 'system mute' if the query is asking to mute or unmute like 'mute the system', 'unmute the system'.
-> Respond with 'system brightness up' if the query is asking to increase screen brightness like 'brightness up', 'increase brightness'.
-> Respond with 'system brightness down' if the query is asking to decrease screen brightness like 'brightness down', 'lower brightness'.
-> Respond with 'system shutdown' if the query is asking to shut down the system like 'shutdown the computer', 'turn off my pc'.
-> Respond with 'system restart' if the query is asking to restart the system like 'restart my pc', 'reboot the computer'.
-> Respond with 'system screenshot' if the query is asking to take a screenshot like 'take screenshot', 'capture screen'.
-> Respond with 'system clipboard' if the query is asking to show clipboard content like 'show clipboard', 'read from clipboard'.
-> Respond with 'system webcam' if the query is asking to open camera or capture webcam like 'take photo from webcam', 'open camera'.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""


def FirstLayerDMM(prompt: str = "test", retries: int = 0, max_retries: int = 3):
    fallback_response = ["general (query)"]

    if retries > max_retries:
        return fallback_response

    if not prompt or not prompt.strip():
        print("[yellow]Empty prompt received. Skipping Cohere call.[/yellow]")
        return fallback_response

    try:
        stream = co.chat_stream(
            model='command-r-plus',
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )

        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        response = response.replace("\n", "").split(",")
        response = [task.strip() for task in response if any(task.strip().startswith(func) for func in funcs)]

        if not response or "(query)" in response[0].lower():
            return FirstLayerDMM(prompt=prompt, retries=retries + 1)

        return response

    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        return fallback_response


if __name__ == "__main__":
    try:
        print("[bold green]Chatbot initialized! Type your queries below. Type 'exit' or 'quit' to end.[/bold green]")
        while True:
            user_input = input(">>> ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("[bold blue]Goodbye![/bold blue]")
                break

            if not user_input.strip():
                print("[yellow]⚠️ Please type something.[/yellow]")
                continue

            try:
                response = FirstLayerDMM(user_input)
                print("[green]Response:[/green]", response)
            except Exception as e:
                print(f"[bold red]❌ Error while processing input: {e}[/bold red]")

    except KeyboardInterrupt:
        print("\n[bold blue]Goodbye![/bold blue]")

