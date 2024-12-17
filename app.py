import ollama
import pyttsx3
import speech_recognition as sr
import re
import base64
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading

def convert_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Fișierul {image_path} nu a fost găsit.")
        return ""
    except Exception as e:
        print(f"Eroare la citirea imaginii: {e}")
        return ""

SYSTEM_PROMPT = """
Acționează ca un asistent OCR.
Trebuie să răspunzi în limba română.
Nu adaugi nicio altă informație în afara răspunsului, incerca sa raspunzi rapid si scurt, nu adauga ceva irelevant.
"""

def listen_for_stop(engine, recognizer, microphone, stop_event):
    print("Debug: Thread-ul de ascultare pentru oprirea conversației a pornit, ascult dupa cuvantul 'gata'...")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    while not stop_event.is_set():
        try:
            with microphone as source:
                recognizer.energy_threshold = 1000  
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=2)
                
                try:
                    interrupt = recognizer.recognize_google(audio, language="ro-RO").lower()
                    
                    if "gata" in interrupt:
                        print("\nDebug: Am detectat cuvântul 'gata'!")
                        stop_event.set()
                        engine.stop()
                        print("Debug: Am oprit engine-ul")
                        break
                except sr.UnknownValueError:
                    pass
                    
        except sr.WaitTimeoutError:
            continue  
        except Exception as e:
            print(f"Debug: Eroare în listen_for_stop: {str(e)}")
            continue
            
def chat_with_ollama(message, image=None):
    current_sentence = ""
    engine = pyttsx3.init()
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    voices = engine.getProperty('voices')
    for voice in voices:
        if "romanian" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 185)
    engine.setProperty('volume', 0.9)

    stop_event = threading.Event()  

    stop_event.clear()
    listen_thread = threading.Thread(target=listen_for_stop, args=(engine, recognizer, microphone, stop_event))
    listen_thread.start()

    try:
        for response in ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': message,
                'images': [image]
            }],
            stream=True
        ):
            if stop_event.is_set():
                print("\nConversatia a fost întreruptă.")
                break

            chunk = response.message.content
            print(chunk, end='', flush=True)
            current_sentence += chunk

            if re.search(r'[.!?]\s*$', current_sentence):
                if current_sentence.strip():
                    engine.say(current_sentence.strip())
                    engine.runAndWait()
                current_sentence = ""  

        if current_sentence.strip():
            engine.say(current_sentence.strip())
            engine.runAndWait()

    except Exception as e:
        print(f"Eroare la procesarea cu Ollama: {e}")
        engine.say("A apărut o eroare în timpul procesării. Te rog să încerci din nou.")
        engine.runAndWait()

    stop_event.set()
    listen_thread.join()

    return current_sentence

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Te rog să vorbești...")
        recognizer.adjust_for_ambient_noise(source) 
        audio = recognizer.listen(source)

    try:
        print("Recunosc mesajul...")
        message = recognizer.recognize_google(audio, language="ro-RO")
        print(f"Mesajul recunoscut: {message}")
        return message
    except sr.UnknownValueError:
        print("Nu am înțeles ce ai spus. Te rog să încerci din nou.")
        engine = pyttsx3.init()
        engine.say("Nu am înțeles ce ai spus. Te rog să încerci din nou.")
        engine.runAndWait()
        return ""
    except sr.RequestError:
        print("Eroare de conexiune cu serviciul de recunoaștere vocală.")
        engine = pyttsx3.init()
        engine.say("Eroare de conexiune cu serviciul de recunoaștere vocală.")
        engine.runAndWait()
        return ""

def interactive_conversation(image=None):
    while True:
        user_message = recognize_speech_from_mic()
        if user_message.lower() == "oprește conversația":
            print("Conversatia s-a încheiat.")
            break

        image_base64 = convert_image_to_base64(image)
        if not image_base64:
            print("Nu am putut încărca imaginea.")
            continue

        response = chat_with_ollama(user_message, image_base64)

        if "oprește" in response.lower():
            engine = pyttsx3.init()
            engine.say("Conversatia s-a încheiat.")
            engine.runAndWait()
            break

class OCRInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Assistant")
        self.image_path = None
        
        # Frame principal
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill='both')
        
        # Buton pentru selectarea imaginii
        self.select_btn = tk.Button(self.main_frame, text="Selectează Imaginea", command=self.select_image)
        self.select_btn.pack(pady=5)
        
        # Label pentru afișarea imaginii
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)
        
        # Buton pentru începerea conversației
        self.start_btn = tk.Button(self.main_frame, text="Începe Conversația", command=self.start_conversation, state='disabled')
        self.start_btn.pack(pady=5)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        if self.image_path:
            image = Image.open(self.image_path)
            image = image.resize((300, 300), Image.Resampling.LANCZOS) 
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            self.start_btn.configure(state='normal')

    def start_conversation(self):
        if self.image_path:
            self.root.withdraw()  
            interactive_conversation(self.image_path)


def main():
    root = tk.Tk()
    app = OCRInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()