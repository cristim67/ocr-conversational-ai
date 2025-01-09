import os
import base64
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from gtts import gTTS
import speech_recognition as sr
import ollama

SYSTEM_PROMPT = """
Ești un asistent vizual care comunică scurt și eficient în limba română.
"""

def say_text_with_gtts(text):
    try:
        tts = gTTS(text=text, lang='ro')
        tts.save("response.mp3")
        if os.name == 'nt':
            os.system("start response.mp3")
        elif os.name == 'posix':
            os.system("mpg123 response.mp3")
        else:
            print("Redare audio indisponibilă pe acest sistem.")
        os.remove("response.mp3")
    except Exception as e:
        print(f"Eroare la redarea audio: {e}")

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    say_text_with_gtts("Salut, cu ce te pot ajuta?")
    print("Debug: Mesajul vocal a fost redat. Pauză înainte de ascultare...")

    with microphone as source:
        print("Te rog să vorbești...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Audio capturat cu succes.")
        except Exception as e:
            print(f"Eroare la capturarea audio: {e}")
            say_text_with_gtts("Nu am reușit să captez vocea ta. Te rog să încerci din nou.")
            return ""

        try:
            print("Recunosc mesajul...")
            message = recognizer.recognize_google(audio, language="ro-RO")
            print(f"Mesajul recunoscut: {message}")
            return message
        except sr.UnknownValueError:
            print("Nu am înțeles ce ai spus. Te rog să încerci din nou.")
            say_text_with_gtts("Nu am înțeles ce ai spus. Te rog să încerci din nou.")
            return ""
        except sr.RequestError as e:
            print(f"Eroare de conexiune cu serviciul de recunoaștere vocală: {e}")
            say_text_with_gtts("Eroare de conexiune cu serviciul de recunoaștere vocală.")
            return ""

def chat_with_ollama(message, image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        formatted_message = f"Te rog să analizezi această imagine și să răspunzi la întrebarea: {message}"
        response = ollama.chat(model="llava", messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatted_message, "images": [image_data]},
        ])

        if not response or not response.message or not response.message.content:
            raise ValueError("Răspuns gol de la model")

        response_text = response.message.content.strip()
        print(response_text)
        say_text_with_gtts(response_text)
        return response_text
    except Exception as e:
        error_msg = f"Eroare la procesarea cu Ollama: {e}"
        print(error_msg)
        print(e.__traceback__)
        say_text_with_gtts("A apărut o eroare în timpul procesării. Te rog să încerci din nou.")
        return ""

def interactive_conversation(image_path):
    while True:
        user_message = recognize_speech_from_mic()
        if user_message.lower() == "oprește conversația":
            say_text_with_gtts("Conversația s-a încheiat.")
            break

        if not image_path:
            say_text_with_gtts("Nu am putut încărca imaginea. Te rog selectează una.")
            continue

        response = chat_with_ollama(user_message, image_path)
        if "oprește" in response.lower():
            say_text_with_gtts("Conversația s-a încheiat.")
            break

class OCRInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Assistant")
        self.image_path = None

        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill='both')

        self.select_btn = tk.Button(self.main_frame, text="Selectează Imaginea", command=self.select_image)
        self.select_btn.pack(pady=5)

        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)

        self.start_btn = tk.Button(self.main_frame, text="Începe Conversația", command=self.start_conversation, state='disabled')
        self.start_btn.pack(pady=5)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if self.image_path:
            display_image = Image.open(self.image_path)
            display_image = display_image.resize((300, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            self.start_btn.configure(state='normal')

    def start_conversation(self):
        if self.image_path:
            self.root.withdraw()
            interactive_conversation(self.image_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRInterface(root)
    root.mainloop()