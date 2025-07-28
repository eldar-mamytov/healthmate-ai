
# HealthMate AI

**HealthMate AI** is an easy-to-use medical chatbot that runs locally on your computer. You can chat about your symptoms and get helpful advice—no programming knowledge needed!

---

- Chat with an AI about your health symptoms (supports **GPT-4**, **FLAN-T5**, and more).
- Text-to-speech (click to hear answers out loud).
- Voice input (microphone support).
- Every login uses one-time account or register your own.
- All data is stored locally (private).
- Works in any browser on your computer.

---

## 🛠 Step-by-Step Setup (For Beginners)

You don’t need to know programming! Just follow these steps:

---

### 1. Install Docker Desktop

- **Windows**:  
  [Download Docker for Windows](https://docs.docker.com/desktop/install/windows-install/)  
  Click "Download for Windows", install the app, restart your computer if needed.  
  Open "Docker Desktop" from the Start menu. Wait until it says **"Docker Desktop is running"**.

- **Mac**:  
  [Download Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)  
  Choose Apple chip or Intel based on your Mac, download the file, and drag Docker to Applications.  
  Open Docker from Applications. Wait until it says **"Docker Desktop is running"**.

✅ *Docker Compose is included with Docker Desktop—no need to install separately.*

---

### 2. Download the Project

- If you don’t use Git:  
  Go to the GitHub page for this project → Click the green **“Code”** button → Select **Download ZIP** → Unzip to your Desktop or any location.

- If you use Git:  
  Open Terminal (Mac) or CMD (Windows) and run:

  ```
  git clone https://github.com/eldar-mamytov/healthmate-ai.git
  ```

  Then navigate into the folder:

  ```
  cd healthmate-ai
  ```

---

### 3. Add Your OpenAI API Key (Optional)

Only needed for GPT-4 features.  
The app still works with FLAN-T5 and embedding models without it.

1. Go to [OpenAI Dashboard](https://platform.openai.com/account/api-keys)  
2. Click "Create API Key" → Copy it  
3. Inside the project folder, create a new file named:

   ```
   .env
   ```

4. Add this line:

   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### 4. Start Docker Desktop

Open **Docker Desktop** (from Start Menu on Windows, or from Applications on Mac).  
Wait until it says **"Docker Desktop is running."**

---

### 5. Start HealthMate AI

- **Windows**:  
  Open Command Prompt → Navigate to the project folder → run:

  ```
  docker-compose up
  ```

- **Mac**:  
  Open Terminal → Navigate to the project folder → run:

  ```
  docker-compose up
  ```

---

### 6. Open the App in Your Browser

Open Chrome, Edge, Firefox, or Safari and go to:  
[http://localhost:3000](http://localhost:3000)

Log in with the default:
- **Username**: `admin`
- **Password**: `admin`  
(or register a new account if you want)

✅ Start chatting with the AI!

---

## 🔁 Stopping & Restarting

To stop the app:
```
Ctrl + C
```

To restart:
```
docker-compose up
```

## 📎 Additional Resources

- 🎥 **Demo Video**: [Watch the screen recording](link-to-your-video-file.mp4)
- 🧪 **AI Pipeline Slides**: [View the pipeline presentation](link-to-your-slides.pptx)