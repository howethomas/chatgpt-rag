from vcon import Vcon
from elasticsearch import Elasticsearch
import streamlit as st
import json

# Pretty print the JSON response
def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))

ELASTIC_SEARCH_CLOUD_ID = st.secrets["ELASTIC_SEARCH_CLOUD_ID"]
ELASTIC_SEARCH_API_KEY = st.secrets["ELASTIC_SEARCH_API_KEY"]
from elasticsearch import Elasticsearch
import json

def get_conversations(q=None, after=None, before=None):
    client = Elasticsearch(
        cloud_id=ELASTIC_SEARCH_CLOUD_ID,
        api_key=ELASTIC_SEARCH_API_KEY
    )

    sort_by = [
        {"_score": {"order": "desc"}},
        {"created_at": {"order": "desc"}},
    ]
    num_hits = 5

    # Combine query and filter clauses efficiently
    body = {
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": q}} if q else {"match_all": {}},
                ] + (
                    [{"range": {"created_at": {"gte": after, "lte": before}}}]
                    if after and before else (
                        [{"range": {"created_at": {"gte": after}}}] if after else (
                            [{"range": {"created_at": {"lte": before}}}] if before else []
                         )
                    )
                )
            }
        }
    }
    print("Querying with body:" + json.dumps(body, indent=2))
    # Execute search and convert hits to Vcon objects
    resp = client.search(index="vcon-index", body=body, size=num_hits, sort=sort_by)
    vcons = [Vcon.from_dict(hit["_source"]) for hit in resp['hits']['hits']]

    # Print the uuids of the vcons
    print([vcon.uuid for vcon in vcons])

    return vcons
