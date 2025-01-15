# Dont Forgot To give Respect To Me(Arya) If you use It 
from PyQt5.QtWidgets import QApplication, QMainWindow,QSpacerItem, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy 
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QBrush
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
GraphicsDirectoryPath = rf"{current_dir}\Frontend\Graphics"
TempDirectoryPath = rf"{current_dir}\Frontend\Files"
Miconpath = rf"C:\Users\techg\OneDrive\Documents\Desktop\Final Project\Frontend\Graphics\Mic_on.png"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer ='\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
    "how", "who", "where", "when", "why", "which", "whose", "whom",
    "what", "can", "could", "would", "should", "is", "are", "was", "were",
    "did", "do", "does", "has", "have", "had", "will", "shall", "may", "might", 
    "am", "might", "must", "please", "can you", "could you", "would you",
    "shall we", "should we", "will you", "is it", "are there", "was there", 
    "were there", "has there", "have there", "did you", "do you", "does it",
    "how much", "how many", "how far", "how long", "how often", "how come",
    "what is", "what are", "what was", "what were", "what do", "what does", 
    "what did", "what can", "what could", "what should", "what will", 
    "what would", "what has", "what have", "what had"
]
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "."
            
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            
    return new_query.capitalize()

if not os.path.exists(TempDirectoryPath):
    os.makedirs(TempDirectoryPath)

def TempDirectoryPath():
    return r"C:\Users\techg\OneDrive\Documents\Desktop\Final Project\Frontend\Files"

def SetMicrophoneStatus(Command):
    temp_dir_path = TempDirectoryPath()
    with open(rf'{temp_dir_path}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    temp_dir_path = TempDirectoryPath()
    with open(rf'{temp_dir_path}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    try:
        temp_dir_path = TempDirectoryPath()
        with open(rf'{temp_dir_path}\Status.data', "w", encoding='utf-8') as file:
           file.write(Status)
    except PermissionError as e:
        print(f"Permission error: {e}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")            

def GetAssistantStatus():
    temp_dir_path = TempDirectoryPath()
    with open(rf'{temp_dir_path}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialized():
    SetMicrophoneStatus("False")  

def MicButtonClosed():
    SetMicrophoneStatus("True")  
    
def GraphicsDirectoryPath(Filename):
    graphics_dir_path = r"C:\Users\techg\OneDrive\Documents\Desktop\Final Project\Frontend\Graphics"
    return rf'{graphics_dir_path}\{Filename}'

def TempDirectoryPath(filename=None):
    base_path = r"C:\Users\techg\OneDrive\Documents\Desktop\Final Project\Frontend\Files"
    if filename:
        return rf"{base_path}\{filename}"
    return base_path

def ShowTextToScreen(Text):
    temp_dir_path = TempDirectoryPath()
    with open(rf'{temp_dir_path}\Response.data',"w",encoding='utf-8') as file:
        file.write(Text)
     
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        self.chat_box = QTextEdit(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        font = QFont("Arial", 14)  
        self.chat_text_edit.setFont(font)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setFixedHeight(400) 
        layout.addWidget(self.chat_text_edit)
        
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.white)
        brush = QBrush(text_color)
        text_color_text = QTextCharFormat()  
        text_color_text.setForeground(brush)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        max_gif_size_W = 800
        max_gif_size_H = 480
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: White; font-size:16px; margin-right:195px; border: none; margin-top: -30px;")
        layout.setAlignment(Qt.AlignRight)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        
        font = QFont()
        font.setPointSize(15)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(1000)

        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: White;
                width: 50px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 10px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-position: margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-position: margin;
                height: 10px;
            }
            QScrollBar::up-arrow: vertical, QScrollBar::down-arrow: vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page: vertical, QScrollBar::sub-page: vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        file_path = TempDirectoryPath('Response.data')
    
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                messages = file.readlines()  
            
                for message in messages:
                    message = message.strip()  
                    if message:  
                        self.addMessage(message=message, color='White')
                        old_chat_message = message  
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            print("Status.data file not found.")
            self.label.setText("Status data not available.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(Miconpath, 60, 60)
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        if not hasattr(self, "_message_history"):
            self._message_history = set()
    
        if message in self._message_history:
            return 
    
        self._message_history.add(message)
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))  
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

            
class InitialScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent) 
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width /16*6)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        pixmap = QPixmap(Miconpath)
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter) 
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("Initial Screen")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
    
    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            print("Status.data file not found.")
            self.label.setText("Status data not available.")
        except Exception as e:
            print(f"An error occurred: {e}")
                
    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)
        else:
            print(f"Error: {path} does not exist.")

            
    def toggle_icon(self , event = None):
        if self.toggled:
            self.load_icon(Miconpath, 60, 60)  
            MicButtonInitialized()
                
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
                
        self.toggled = not self.toggled
        
from PyQt5.QtGui import QGuiApplication        
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        max_gif_size_H = int(screen_width*screen_height /16*6)
        layout = QVBoxLayout()
        label = QLabel("Welcome to the Chat Section")
        label.setStyleSheet("color: Red; font-size: 30px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        chat_section = ChatSection() 
        layout.addWidget(chat_section)
        layout.addItem(spacer)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: Black;")
        self.showFullScreen()
               
class CustomTopBar(QWidget):
    def __init__(self, parent , stacked_widget):
        super().__init__(parent) 
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget
        
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight) 
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))  
        home_button.setIcon(home_icon)
        home_button.setText("  Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color:black;") 
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))  
        message_button.setIcon(message_icon)
        message_button.setText("  Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color:black;") 
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))  
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white;") 
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))  
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white;") 
        self.maximize_button.clicked.connect(self.minimizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath("close.png"))  
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white;") 
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color:black;")
        title_lable = QLabel(f"{str(Assistantname).capitalize()} AI   ")
        title_lable.setStyleSheet("color: black; font-size:18px; background-color:white;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_lable)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
        
    def minimizeWindow(self):
        self.parent().showMinimized()
        
    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
            
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)      
            
    def closeWindow(self):
        self.parent().close()
        
    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()    
        
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos) 
            
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
            
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen
        
    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
            
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen
       
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() 
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        Message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(Message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()        
    sys.exit(app.exec_())
    
if __name__ =="__main__":
    GraphicalUserInterface()
        

                
                                            
        
        
        
            
            
                                     
               