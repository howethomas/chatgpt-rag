"""
Elastic Search / vCons

"""
import streamlit as st
from elasticsearch import Elasticsearch
from vcon import Vcon
from datetime import datetime
import uuid as uuidlib
import streamlit as st
import numpy as np
import pandas as pd
import json

ELASTIC_SEARCH_CLOUD_ID = st.secrets["ELASTIC_SEARCH_CLOUD_ID"]
ELASTIC_SEARCH_API_KEY = st.secrets["ELASTIC_SEARCH_API_KEY"]
CONV_DETAIL_URL = st.secrets["CONV_DETAIL_URL"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
INSTRUCTIONS = st.secrets["INSTRUCTIONS"]

def get_conversations(q, after=None, before=None):
    client = Elasticsearch(
        cloud_id=ELASTIC_SEARCH_CLOUD_ID,
        api_key=ELASTIC_SEARCH_API_KEY
    )
    sort_by = [
                {
                    "_score": {
                        "order": "desc"
                    }
                },
                {
                    "created_at": {
                        "order": "desc"  # Sorting by 'created_at' in descending order
                    }
                }]
    num_hits = 5
    resp = client.search(
        index="vcon-index", 
        body={ 
            "query": {
                "bool": {
                    "must": [{ 
                    "query_string": {
                            "query": q
                        }}]
                    }
                },
            "highlight": {
                "fields": {
                    "agent": {},
                    "agent.keyword": {},
                    "analysis": {},
                    "analysis.body": {},
                    "analysis.type": {},
                    "analysis.type.keyword": {},
                    "analysis.vendor": {},
                    "attachments.body": {},
                    "attachments.type": {},
                    "created_at": {},
                    "dealer_id": {},
                    "dialog": {},
                    "dialog.meta.direction": {},
                    "dialog.meta.disposition": {},
                    "parties.mailto": {},
                    "parties.meta.extension": {},
                    "parties.meta.role": {},
                    "parties.name": {},
                    "parties.tel": {},
                    "team_id": {},
                    "updated_at": {},
                    "uuid": {},
                    }
            },
            "size": num_hits,
            "sort": sort_by
            }
        )
    st.write("Got response: ")
    st.json(resp)
    vcons = []
    for hit in resp['hits']['hits']:
        vcon = Vcon.from_dict(hit["_source"])
        vcons.append(vcon)
    return vcons

st.title("Strolid GPT!")
st.caption("Connects GPTs to vCons")

from openai import OpenAI
import time
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
    st.write(f"Assistant created: {assistant.name}")

# Create a new thread if one does not exist
if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()
    st.session_state.messages = []

# Get the thread
thread = client.beta.threads.retrieve(thread_id=st.session_state.thread.id)


# Add the new messages to the chat
messages = st.session_state.messages
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if prompt := st.chat_input("What is up?"):
    # Add the message to the chat
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
        )
    
    # Wait for the run to complete
    # Show a progress bar while waiting
    with st.spinner('Wait for it...'):
        status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        while status.status != "completed":
            time.sleep(1)  # Add a 1-second delay between status retrievals
            status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if status.status == "requires_action":
                if status.required_action.type == "submit_tool_outputs":
                    for call in status.required_action.submit_tool_outputs.tool_calls:
                        if call.function.name == "get_conversation":
                            tool_call_id = call.id
                            arguments = json.loads(call.function.arguments)
                            q = arguments.get("q")
                            after = arguments.get("after")
                            before = arguments.get("before")
                            vcons = get_conversations(q, after, before)
                            # Submit the tool outputs
                            json_vcons = [vcon.to_json() for vcon in vcons]
                            client.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=[
                                    {
                                        "tool_call_id": tool_call_id,
                                        "output": json.dumps(json_vcons)
                                    }
                                ]
                            )
                            


    # Get the message from the assistant
            
    # Print out the run step object
    steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    for step in steps:
        step_details = step.step_details
        if step_details.type == "message_creation":
            message_id = step.step_details.message_creation.message_id
            message = client.beta.threads.messages.retrieve(
                thread_id=thread.id,
                message_id=message_id
            )
            message_content = message.content[0].text
            with st.chat_message("assistant"):
                st.markdown(message_content.value)
            st.session_state.messages.append({"role": "assistant", "content": message_content.value})
        else:
            message_id = None
            print("No message id found")


