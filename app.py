import json
import gradio as gr
from neo4j import GraphDatabase
import requests
import logging
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
with open('config/settings.json') as f:
    config = json.load(f)
NEO4J_URL = config['neo4j_url']
NEO4J_USER = config['neo4j_user']
NEO4J_PASSWORD = config['neo4j_password']
NEO4J_DATABASE = config['neo4j_database']
OLLAMA_URL = config['ollama_url']
MODEL = config['ollama_model']

def connect_to_neo4j():
    try:
        driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        logger.info("Connected to Neo4j")
        return driver
    except Exception as e:
        logger.error(f"Neo4j connection failed: {str(e)}")
        raise

def call_ollama(entry, memory):
    try:
        prompt = f"""
        Analyze this journal entry: {entry}
        Past context: {memory}
        Return a single JSON object with:
        {{
        "sentiment": "positive/negative/neutral",
        "summary": "short summary",
        "suggestions": ["suggestion1", "suggestion2"],
        "themes": ["theme1", "theme2"],
        "goals": ["goal1"]
        }}
        """
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            return json.loads(data["response"])
        logger.error(f"Unexpected Ollama response: {data}")
        return None
    except Exception as e:
        logger.error(f"Ollama error: {str(e)}")
        return None
    

def store_in_neo4j(driver, entry, result):
    def create_nodes(tx, entry, result):
        timestamp = datetime.now().isoformat()
        entry_id = f"entry_{timestamp.replace(':', '-')}"
        tx.run("CREATE (e:Entry {id: $entry_id, text: $text, date: $date})", 
               entry_id=entry_id, text=entry, date=timestamp)
        if result.get("sentiment"):
            tx.run("MERGE (em:Emotion {type: $sentiment}) MERGE (e:Entry {id: $entry_id}) MERGE (e)-[:EXPRESSES]->(em)", 
                   sentiment=result["sentiment"], entry_id=entry_id)
        for theme in result.get("themes", []):
            tx.run("MERGE (t:Theme {name: $theme}) MERGE (e:Entry {id: $entry_id}) MERGE (e)-[:CONTAINS]->(t)", 
                   theme=theme, entry_id=entry_id)
        for suggestion in result.get("suggestions", []):
            tx.run("MERGE (s:Suggestion {text: $suggestion}) MERGE (e:Entry {id: $entry_id}) MERGE (e)-[:HAS_SUGGESTION]->(s)", 
                   suggestion=suggestion, entry_id=entry_id)
        for goal in result.get("goals", []):
            tx.run("MERGE (g:Goal {text: $goal}) MERGE (e:Entry {id: $entry_id}) MERGE (e)-[:SETS]->(g)", 
                   goal=goal, entry_id=entry_id)
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            session.execute_write(create_nodes, entry, result)
        logger.info(f"Stored entry: {entry[:50]}...")
    except Exception as e:
        logger.error(f"Neo4j storage error: {str(e)}")

def get_memory(driver):
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (em:Emotion) RETURN em.type AS emotion, count(*) AS count ORDER BY count DESC LIMIT 5")
            emotions = [f"{record['emotion']} ({record['count']}x)" for record in result]
            return ", ".join(emotions) if emotions else "No past emotions"
    except Exception as e:
        logger.error(f"Memory error: {str(e)}")
        return "Error retrieving memory"



def main():
    driver = connect_to_neo4j()
    
    def process_entry(entry, chat_history):
        if not entry:
            return chat_history, "Please enter a journal entry.", ""
        memory = get_memory(driver)
        result = call_ollama(entry, memory)
        if not result:
            raise Exception("Ollama failed to process entry")
            # result = {"sentiment": "test", "summary": "Test summary", "suggestions": ["Test"], "themes": ["test"], "goals": []}
        store_in_neo4j(driver, entry, result)
        response = (
            f"**Sentiment**: {result.get('sentiment', 'unknown')}\n"
            f"**Summary**: {result.get('summary', 'N/A')}\n"
            f"**Suggestions**: {', '.join(result.get('suggestions', []))}\n"
            f"**Themes**: {', '.join(result.get('themes', []))}\n"
            f"**Goals**: {', '.join(result.get('goals', []))}"
        )
        chat_history.append({"role": "user", "content": entry})
        chat_history.append({"role": "assistant", "content": response})
        updated_memory = get_memory(driver)
        logger.info(f"Processed entry: {entry[:50]}...")
        return chat_history, "", updated_memory

    with gr.Blocks() as iface:
        chatbot = gr.Chatbot(label="JournalSync", type="messages")
        entry = gr.Textbox(label="Journal Entry", placeholder="Write your journal entry here...")
        memory = gr.Textbox(label="Memory", value=get_memory(driver), interactive=False)
        submit = gr.Button("Submit")
        submit.click(process_entry, inputs=[entry, chatbot], outputs=[chatbot, entry, memory])
    iface.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()