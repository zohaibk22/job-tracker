# 📬 AI Job Application Tracker

A Python-based automation tool that uses **LangGraph**, **Gmail**, **OpenAI GPT**, and **Google Sheets** to extract job application emails from your inbox and log them into a spreadsheet.

---

## 🚀 Features

- 📅 Automatically fetches emails received **today**
- 🤖 Uses GPT to identify job-related emails (e.g., submissions, rejections)
- 🧠 Extracts structured data:
  - Company name
  - Job title
  - Date
- 📊 Appends the data to a **Google Sheet**
- 🧩 Built with modular **LangGraph agents**

---

## 🧰 Tech Stack

- [LangGraph](https://www.langgraph.dev/) – multi-agent orchestration
- [Langchain](https://www.langchain.com/) – prompt interface
- [OpenAI API](https://platform.openai.com/)
- [Gmail API](https://developers.google.com/gmail/api)
- [Google Sheets API](https://developers.google.com/sheets/api)
- Python 3.9+

---

## 🏗 Project Structure

email-to-sheet-bot/
├── agents/
│ ├── email_fetcher.py # Fetch today's Gmail emails
│ ├── classifier_agent.py # AI: Is this job-related?
│ ├── extractor_agent.py # AI: Extract job info
│ └── sheet_writer.py # Write data to Google Sheets
├── utils/
│ └── gmail_auth.py # Gmail OAuth helper
├── credentials/
│ ├── credentials.json # Google OAuth client ID
│ └── token.pkl # Auto-generated after login
├── graph.py # LangGraph flow definition
├── main.py # Entrypoint to run the agents
├── .env # OpenAI key and config
└── requirements.txt # Python dependencies



## 🛠 Setup Instructions

### 1. Gmail + Sheets API

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Enable **Gmail API** and **Google Sheets API**
- Create an **OAuth 2.0 client ID** for a **desktop app**
- Download `credentials.json` and place it in `credentials/`

### 2. Add Yourself as a Test User

- Go to `APIs & Services > OAuth consent screen`
- Add your Gmail under **Test Users**
- Keep app in **Testing** mode

### 3. Install Requirements

```bash
pip install -r requirements.txt 
