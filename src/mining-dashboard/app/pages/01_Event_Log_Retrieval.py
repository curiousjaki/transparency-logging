from elasticsearch7 import Elasticsearch
import numpy as np
import pandas as pd
import json
import streamlit as st

combined_df = None

st.title("Event Log Retrieval")
st.write("This can be used to retrieve an TILT extended event log from an Elasticsearch 7.9.1 instance.")
progress_text = "Ready for retrieval"
my_bar = st.progress(0, text=progress_text)
st.code("Production: \n http://elasticsearch.elastic-kibana:9200 \nDevelopment: \n http://localhost:9200")
host = st.text_input("Enter the available host here:","http://localhost:9200")
result = st.button("Retrieve from Host")

if result and not combined_df:

    my_bar.progress(10, text = f"Connecting to {host}.")
    es = Elasticsearch(hosts=host)

    my_bar.progress(15, text = f"Retrieving index information")
    response = es.search(index="fluentd-k8s",)
    hit_count = response["hits"]["total"]["value"]
    #st.write(f"Found {hit_count} log entries.")
    my_bar.progress(20, text = f"Downloading index ...")
    response = es.search(index="fluentd-k8s", size=hit_count)
    docs = response["hits"]["hits"]
    fields = {}
    for num, doc in enumerate(docs):
        my_bar.progress(int(20+num/len(docs)*70), text = f"Building Field {num}/{len(docs)}")
        source_data = doc["_source"]
        for key, val in source_data.items():
            if key == "log":
                try:
                    fields[key] = np.append(fields[key], val)
                except KeyError:
                    fields[key] = np.array([val])

    my_bar.progress(92, text = f"Creating Data Frame")
    df : pd.DataFrame = pd.DataFrame(fields)
    log_df : pd.DataFrame = pd.json_normalize(df["log"].apply(json.loads))
    my_bar.progress(98, text = f"Converting JSON information in log")
    tilt_df : pd.DataFrame = pd.json_normalize(
        log_df["tilt"]
        .apply(lambda x: x.replace("\'","\""))
        .apply(json.loads))\
            .add_prefix("tilt:")

    combined_df = pd.concat([log_df,tilt_df],axis=1).drop("tilt",axis=1)
    combined_df.index.name = "ident:eid"
    combined_df.to_csv("tilt-enhanced-event-log.csv",sep=",")
    my_bar.progress(100, text = f"Event log is ready for download.")
    st.session_state["df"] = combined_df
    st.success("The retrieved event log is stored in the session.")
    combined_df.to_csv("/tmp/transparency_event_log.csv",sep=",")
    with open("/tmp/transparency_event_log.csv") as f:
        csv = f.read()
        f.close()
    st.download_button("Download csv event log",data=csv,file_name="transparency_event_log.csv")