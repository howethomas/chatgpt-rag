import streamlit as st
from openai import OpenAI

ELASTIC_SEARCH_CLOUD_ID = st.secrets["ELASTIC_SEARCH_CLOUD_ID"]
ELASTIC_SEARCH_API_KEY = st.secrets["ELASTIC_SEARCH_API_KEY"]
CONV_DETAIL_URL = st.secrets["CONV_DETAIL_URL"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
INSTRUCTIONS = st.secrets["INSTRUCTIONS"]

def get_assistant():
    client = OpenAI(api_key=OPENAI_API_KEY)
    version  = 1.0
    assistant_name = "Strolid GPT"
    st.write(f"Version: {version}")

    # Check to see if the assistant exists
    assistants = client.beta.assistants.list()
    assistant = None
    for a in assistants:
        if a.name == assistant_name:
            assistant = a
            break

    if not assistant:
        st.write(f"Creating assistant: {assistant_name}")
        assistant = client.beta.assistants.create(
            instructions=INSTRUCTIONS,
            name="Strolid GPT",
            tools=[
                {
                "type": "function",
                "function": {
                    "name": "get_conversation",
                    "description": "returns summaries and identifiers for conversations that match search criteria",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "q": {
                            "type": "string",
                            "description": "Search term to find conversations. Can be name, phone number, id, words said. Assumes daterange of the past seven days unless specified by after or before."
                        },
                        "after": {
                            "type": "string",
                            "description": "Return conversations after this date time, expressed in an ISO 8601 format. Can be combined with before to specify a window of time."
                        },
                        "before": {
                            "type": "string",
                            "description": "Return conversations before this date time, expressed in an ISO 8601 format. Can be combined with after to specify a window of time"
                        }
                        },
                        "required": [
                        "q"
                        ]
                    }
                }
            }],
            model="gpt-4",
        )
    return client, assistant