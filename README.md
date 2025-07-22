**LLaMA MindMap**
A simple AI-powered mindmap application that uses Hugging Face models to expand topics, generate steps, and analyze content. Built with Flask for easy deployment and use.
**Quick Start**

Clone or download this project
Add your Hugging Face token to .env file
Double-click run.bat to start the application
Open http://localhost:5000 in your browser

**Features**

Topic Expansion: Break down any topic into subtopics using AI
Step Generation: Get actionable steps for completing tasks
Topic Analysis: Receive intelligent analysis and insights
Responsive Design: Works on desktop and mobile devices
Simple API: Clean REST endpoints for integration

**Installation Prerequisites**

Python 3.9 or higher
Hugging Face account (free)


Configure Application:

Open .env file
Replace your_huggingface_token_here with your actual token:

HUGGINGFACE_TOKEN=**hf_your_actual_token_here**

**Start Application:**

Windows: run windows_venv.bat run.py
Linux/Mac: Run python run.py



Usage
Web Interface

Open http://localhost:5000
Enter any topic (e.g., "Learn Python", "Start a Business")
Click buttons to:

Expand: Break into subtopics
Steps: Generate action steps
Analyze: Get detailed analysis


# Optional: Change these if needed
FLASK_RUN_PORT=5000
HUGGINGFACE_MODEL= **add supported model here**
DEBUG=true
```
**Project Structure**
llama-mindmap/
├── windows_venv.bat           # Windows startup script
├── run.py                     # Application entry point
├── .env                       # Configuration file
├── requirements.txt           # Dependencies
├── templates/                 # HTML pages
│   ├── index.html            # Desktop version
│   └── index_mobile.html     # Mobile version
├── static/                    # CSS, JS, images
│   ├── css/style.css
│   └── js/app.js
└── llama_mindmap_backend/     # Python application
    ├── __init__.py           # App factory
    ├── config.py             # Settings
    └── routes/               # API endpoints
```

**Troubleshooting**
**_Application won't start:_**
Check Python is installed: python --version
Install dependencies: pip install -r requirements.txt

_**API not working:**_

Verify Hugging Face token in .env file
Check internet connection
Visit /api/web/test to test connection

_**Templates not loading:**_

Ensure templates/index.html exists
Check file permissions

Development
To modify or extend the application:

Add new features: Edit files in llama_mindmap_backend/
Change UI: Modify templates/ and static/ files
Add API endpoints: Update routes/web_api.py

for prerequiments check:
requirements.txt

**License**
MIT License - feel free to use and modify.


--------------------------------------------------------------
Simple AI mindmapping made easy. No complex setup required.
