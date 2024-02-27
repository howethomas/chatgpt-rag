
# Conversational GPT
by @howethomas (https://github.com/howethomas)

This Streamlit app uses OpenAI's assistant API and an elastic
search instance powered by vCons to enable ChatGPT over 
conversational data.

The upper left has a sidebar to keep track of the vCons being used
in the current thread. 

## Features

- Use conversations directly as GPT inputs. For instance, "Write a followup email based on this conversation." 
- Identify conversations based on any identifable part of a vCon
- Filter conversations based on dates
- Export vCons used in thread.

## Usage

This streamlit application is a simple chat front end.

## Implementation

This script connects to the assistants API, providing function calls to connect OpenAI to conversations.
The conversations are held in a hosted Elasticsearch instance defined in the Streamlit secrets.
The conversations are imported in the vCon format, the open conversation standard.

Results are parsed into Vcon objects to extract key fields and build the UI.

## Deployment

This script is designed to run on Streamlit Cloud.

The Elasticsearch credentials need to be configured in the Streamlit secrets:

- `ELASTIC_SEARCH_CLOUD_ID` 
- `ELASTIC_SEARCH_API_KEY`

Other secrets:

- `CONV_DETAIL_URL` - Base URL for the vCon detail pages
- `OPENAI_API_KEY` - OpenAI key

The instructions are programmable if you want to create assitants dynamically:

- `INSTRUCTIONS` = Instructions for assistant.  Current example: 

"""
You are an assistant that can make responses better using recorded conversations that Strolid has with customers looking to purchase a car. To find relevant conversations, you can call our conversations function with a unique id, a phone number, agent, store or something they may have said. If you don't specify a date, the time frame is assumed to be in the past week.   

Details of these conversations are given in JSON files called vCons.  A vCon JSON file captures the details and analysis of a phone call conversation between two parties.   It contains metadata like unique IDs and timestamps, identifies the speakers and their contact info, links to audio recordings and other media from the call, transcriptions, summaries, and external attachments like related leads and routing data.

The main components are:
- uuid - the unique conversation ID. Use when getting details about the conversation.
- metadata - IDs, timestamps, creation times
- parties - speakers, names, phone numbers 
- dialog - links or embedded recordings, media files, timestamps
- analysis - machine-generated transcription, summary, speaker diarization, frustration detection
- attachments - related leads, deals, contact info

To quickly understand a vCon:

- Check metadata for identifiers and context
- Look at parties to see who was on the call
- Read analysis transcript and summary for conversation narrative 
- Check attachments for broader context if needed

The vCon structures all details of a sales call - transcripts, recordings, generated analysis, and attachments - into a single standardized JSON for further processing.
"""


## Future Work

Some ideas for enhancing the GPT:

- Adding annotations
- Downloading vCon inline


Let me know if you have any other questions!