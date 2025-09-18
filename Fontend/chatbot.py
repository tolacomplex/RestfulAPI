from PyQt6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit
)
import sys, os
import requests as req
from PyQt6.QtCore import QThread, pyqtSignal

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# from Backend.main import Chatbot  # Unused import removed

class BotWorker(QThread):
    reply_ready = pyqtSignal(str)

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            response = req.post(
                "http://127.0.0.1:8000/chat/",
                json={"message": self.user_input}
            )
            reply = response.json().get("reply", "No reply")
        except Exception as e:
            reply = f"Error: {e}"
        self.reply_ready.emit(reply)


class ChatbotMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # self.chatbot = Chatbot()  # Unused, removed
        
        self.setMinimumSize(500, 600)
        self.setWindowTitle("Nu Chatbot Assistant")

        page_widget = QWidget()
        page_widget.setStyleSheet("background-color: black")
        self.setCentralWidget(page_widget)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("""
            QTextEdit {
                border-radius: 10px;
                background-color: white;
                padding: 10px;
                border: 1px solid black;
            }
        """)

        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Type something…")
        self.input_text.setStyleSheet("""
            QLineEdit {
                background-color: gray;
                padding: 10px;
                border-radius: 20px;
                border: 1px solid black;
            }
        """)
        self.input_text.returnPressed.connect(self.send_message)

        self.button_send = QPushButton("Send")
        self.button_send.setFixedSize(60, 40)
        self.button_send.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                background-color: #845ec2;
                color: white;
                border: none;
            }
        """)
        self.button_send.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        layout.addWidget(self.output_display)
        h_layout.addWidget(self.input_text)
        h_layout.addWidget(self.button_send)
        layout.addLayout(h_layout)

        page_widget.setLayout(layout)

        self.workers = []  # Keep references to workers

    def send_message(self):
        user_input = self.input_text.text().strip()
        if not user_input:
            return
        self.output_display.append(
            "<p style='color:black;font-size:13pt;font-family:georgia;line-height:1.5'>"
            f"<b>Me:</b> {user_input}</p>"
        )
        self.input_text.clear()

        # Start API worker thread
        worker = BotWorker(user_input)
        worker.reply_ready.connect(self.display_reply)
        worker.finished.connect(lambda: self.workers.remove(worker))
        self.workers.append(worker)
        worker.start()

    def display_reply(self, reply):
        formatted_response = (
            "<p style='color:black;font-size:13pt;font-family:georgia;line-height:1.5'>"
            "<b>Bot:</b> " + reply.replace("\n", "<br>") + "</p>"
        )
        self.output_display.append(formatted_response)

def main():
    app = QApplication(sys.argv)
    window = ChatbotMain()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()