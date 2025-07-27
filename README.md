HealthMate AI

HealthMate AI is an easy-to-use medical chatbot that runs locally on your computer. You can chat about your symptoms and get helpful advice—no programming knowledge needed!

⸻

Features
	•	Chat with an AI about your health symptoms (supports GPT-4, FLAN-T5, and more)
	•	Text-to-speech (click to hear answers out loud)
	•	Voice input (microphone support)
	•	Easy login: use demo account or register your own
	•	All data is stored locally (private)
	•	Works in any browser on your computer

⸻

Step-by-Step Setup (For Beginners)

You don’t need to know programming! Just follow the steps.

⸻

1. Install Docker Desktop

For Windows:
	•	Go to https://www.docker.com/products/docker-desktop/
	•	Click “Download for Windows”
	•	Open the downloaded file and follow the instructions to install
	•	Restart your computer if asked
	•	Open Docker Desktop from the Start menu
	•	Wait until it says “Docker Desktop is running”

For Mac:
	•	Go to https://www.docker.com/products/docker-desktop/
	•	Click “Download for Mac” (choose Apple Chip or Intel based on your Mac)
	•	Open the downloaded file and drag Docker to Applications
	•	Open Docker from Applications
	•	Wait until it says “Docker Desktop is running”

Docker Compose is included with Docker Desktop—you do not need to install it separately.

⸻

2. Download the Project

If you don’t use Git:
	•	Go to the GitHub page for this project.
	•	Click the green “Code” button, then “Download ZIP”.
	•	Unzip the folder to your Desktop or another location.

If you use Git:
	•	For Windows:
cmd: git clone https://github.com/eldar-mamytov/healthmate-ai.git
cmd: cd Desktop\healthmate-ai
	•	For Mac:
terminal: git clone https://github.com/eldar-mamytov/healthmate-ai.git
terminal: cd ~/Desktop/healthmate-ai

⸻

3. Add Your OpenAI API Key (optional)
	•	This is only needed for GPT-4 features. The app will work with FLAN-T5 and embedding models even if you skip this.
	•	Go to https://platform.openai.com/api-keys and create a new secret key.
	•	Copy the key.
	•	Open the file named .env in the project folder with Notepad (Windows) or TextEdit/VSCode (Mac).
	•	Find the line that says:
OPENAI_API_KEY=
Paste your key after the =, like this:
OPENAI_API_KEY=sk-xxxxxxxYOURKEY
	•	Save the file.

⸻

4. Start Docker Desktop

Open Docker Desktop (from Start Menu on Windows, or from Applications on Mac).
Wait until it says “Docker Desktop is running”.

⸻

5. Start HealthMate AI
	•	Open Command Prompt (Windows) or Terminal (Mac)
	•	Go to the folder where you unzipped or cloned the project.
For Windows:
    cmd: cd Desktop\healthmate-ai
For Mac:
    terminal: cd ~/Desktop/healthmate-ai
	•	Start the app:
For Windows:
    cmd: docker-compose up –build
For Mac:
    terminal: docker-compose up –build

⸻

6. Open the App in Your Browser
	•	Open Chrome, Edge, Firefox, or Safari on your computer.
	•	Go to: http://localhost:3000
	•	Log in with the demo account:
Username: eldar
Password: eldar
(Or you can register a new account if you want.)
	•	Start chatting with the AI!

⸻

Stopping & Restarting

To stop:
	•	In your terminal or command prompt, press Ctrl + C

To restart:
	•	Run the docker-compose up –build command again

⸻

Resetting the Database (Advanced)
	•	Stop the app first (Ctrl + C)
	•	Then run:
For Windows:
cmd: docker-compose down -v
For Mac:
terminal: docker-compose down -v
	•	Then start as usual.

⸻

About

Built with FastAPI, React, PostgreSQL, Docker, OpenAI, and FLAN-T5.