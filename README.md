# Journaling-Chatbot

## Overview
Journaling-Chatbot is an AI-powered journaling tool designed to help users reflect on their emotions and experiences. Built with Gradio for an interactive interface, it leverages the Llama 3 model via Ollama for sentiment analysis and stores entries in Neo4j Aura, a cloud-based graph database. This project allows users to input journal entries, receive AI-generated insights (sentiment, summary, suggestions, themes, and goals), and track their emotional history.
Features

Interactive Interface: A Gradio-based chat interface for seamless entry submission.
AI Sentiment Analysis: Utilizes Ollama with Llama 3 to analyze emotions and provide insights.
Data Storage: Stores journal entries and emotional data in Neo4j Aura.
Memory Tracking: Displays past emotional trends to provide context for new entries.

Prerequisites

- Ubuntu 22.04 or 24.04 (or compatible Linux distribution)
- Python 3.8+
- Git for version control
- Ollama with Llama 3 model
- Neo4j Aura account

Installation
1. Clone the Repository
```
git clone https://github.com/yourusername/JournalSync.git
cd JournalSync
 ```

2. Set Up Virtual Environment
 ```
 python3 -m venv venv
 source venv/bin/activate
 pip install gradio requests neo4j pandas
```

4. Configure Environment

```
Create a config/settings.json file:{
  "neo4j_url": "neo4j+s://<Enter your ID>.databases.neo4j.io",
  "neo4j_user": "neo4j",
  "neo4j_password": "<Enter your own password>",
  "neo4j_database": "neo4j",
  "ollama_url": "http://localhost:11434/api/generate",
  "ollama_model": "llama3"
}

```

5. Install and Configure Ollama

    Install Ollama:
   ```
   curl -fsSL https://ollama.com/install.sh | sh
   ```


Download Llama 3:
    `ollama pull llama3`


Set up as a systemd service (optional): `sudo nano /etc/systemd/system/ollama.service`

```
Add:[Unit]
Description=Ollama Service
After=network.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
User=den
Environment="HOME=/home/den"
Environment="OLLAMA_HOST=0.0.0.0:11434"
StandardOutput=journal
StandardError=journal
TimeoutStartSec=30

[Install]
WantedBy=multi-user.target

Enable and start:sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

Usage

Activate the virtual environment:source venv/bin/activate


Run the application: `python app.py`


Open your browser and navigate to http://127.0.0.1:7860.
Enter a journal entry in the text box and click "Submit" to see AI-generated insights.

<img width="1593" height="754" alt="Screenshot from 2025-09-06 19-45-27" src="https://github.com/user-attachments/assets/eb792058-877b-4b01-b92a-47c15bbba986" />

<img width="1593" height="754" alt="Screenshot from 2025-09-06 19-41-45" src="https://github.com/user-attachments/assets/ccad46ef-bb2e-48e4-8cc7-18edf76313a7" />

Contributing
Feel free to fork this repository and submit pull requests. Please ensure any changes are tested and documented.
License
[MIT License] - See the LICENSE.md file for details (create this file if needed).
Acknowledgements

Gradio for the interactive UI framework.
Ollama and Llama 3 for AI capabilities.
Neo4j Aura for graph database support.
