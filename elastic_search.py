from vcon import Vcon
from elasticsearch import Elasticsearch
from datetime import datetime
import streamlit as st

ELASTIC_SEARCH_CLOUD_ID = st.secrets["ELASTIC_SEARCH_CLOUD_ID"]
ELASTIC_SEARCH_API_KEY = st.secrets["ELASTIC_SEARCH_API_KEY"]

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
    vcons = []
    for hit in resp['hits']['hits']:
        vcon = Vcon.from_dict(hit["_source"])
        vcons.append(vcon)
    return vcons