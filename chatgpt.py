"""
Elastic Search / vCons

"""
import streamlit as st
import json
import time
import openai_lib
from datetime import datetime

from elastic_search import get_conversations

ELASTIC_SEARCH_CLOUD_ID = st.secrets["ELASTIC_SEARCH_CLOUD_ID"]
ELASTIC_SEARCH_API_KEY = st.secrets["ELASTIC_SEARCH_API_KEY"]
CONV_DETAIL_URL = st.secrets["CONV_DETAIL_URL"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
INSTRUCTIONS = st.secrets["INSTRUCTIONS"]


st.title("Strolid GPT!")
st.caption("Connects GPTs to vCons")

client, assistant = openai_lib.get_assistant()

# Create a new thread if one does not exist
if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()
    st.session_state.messages = []
    st.session_state.vcons = []


# In the sidebar, show the vConIDs that are used in this conversation, 
# and provide a link to the vCon detail page using the vConID and CONV_DETAIL_URL
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
                    print("Submit tool outputs")
                    for call in status.required_action.submit_tool_outputs.tool_calls:
                        if call.function.name == "get_conversation":
                            print("Get conversation: " + call.id)
                            tool_call_id = call.id
                            arguments = json.loads(call.function.arguments)
                            print("Arguments: " + str(arguments))
                            q = arguments.get("q")
                            after = arguments.get("after")
                            before = arguments.get("before")
                            details = arguments.get("details")
                            vcons = get_conversations(q, after, before)

                            # Submit the tool outputs
                            if details:
                                print("Giving details")
                                json_vcons = [vcon.to_json() for vcon in vcons]
                                output = json.dumps(json_vcons)
                            else:
                                print("Summarizing")
                                summaries = [vcon.get_summary() for vcon in vcons]
                                output = "\n\n".join(summaries)

                            client.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=[
                                    {
                                        "tool_call_id": tool_call_id,
                                        "output": output
                                    }
                                ]
                            )

                            # Add the vcons to the session state
                            st.session_state.vcons.extend(vcons)

                            # # Add the vcons to the sidebar
                            # for vcon in vcons:
                            #     st.sidebar.markdown(f"[{vcon.created_at}]({CONV_DETAIL_URL}\"{vcon.uuid}\")")

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

show_debug_info = st.checkbox("Show debug info")
if show_debug_info:
    st.write("Thread ID: " + thread.id)
    st.write("Assistant ID: " + assistant.id)
    st.write("Messages: " + str(st.session_state.messages))
    st.write("vCons: " + str(st.session_state.vcons))