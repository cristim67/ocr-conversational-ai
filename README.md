# Voice-Enabled OCR Assistant

An intelligent OCR assistant that can analyze images and communicate results through voice, using the llama3.2-vision model and graphical interface.

## Features

- Graphical interface for image uploading
- Optical Character Recognition (OCR)
- Two-way voice communication (Text-to-Speech and Speech-to-Text)
- Romanian language support
- Ability to interrupt conversation using the word "done"

## System Requirements

- [Python 3.10+](https://www.python.org/downloads/)
- [Ollama](https://ollama.ai/) with [llama3.2-vision model](https://ollama.ai/models/llama3.2-vision) installed
- Working microphone
- Speakers or headphones

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cristim67/proiect-iom.git
```
2. Create a virtual environment:
```bash 
python -m venv venv
```
3. Activate the virtual environment:
```bash
source venv/bin/activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Run the application:
```bash
python app.py
```

## Usage

1. Upload an image using the graphical interface.
2. Start the conversation by speaking or clicking the "Start" button.
3. Interrupt the conversation by saying "stop" or "gata".
4. The assistant will analyze the image and respond through voice.

## Note

- The application is designed to work with Romanian language.