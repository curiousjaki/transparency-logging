import streamlit as st
import pandas as pd
import pm4py
import pm4py.visualization.bpmn.visualizer as bpmnvs

#from io import StringIO
from discovery_functions import \
    append_tilt_information_to_bpmn,\
    get_data_disclosed_df

st.title("Process Discovery")
progress_text = "Please upload a TILT extended Event Log"
my_bar = st.progress(0, text=progress_text)
c1, c2 = st.columns((5, 1))
with c1:
    uploaded_file = st.file_uploader("Choose a Tilt extended event log file")
with c2:
    st.text("")
    st.text("")
    disabled = True
    if "df" in st.session_state.keys():
        if type(st.session_state["df"]) == pd.DataFrame:
            if not st.session_state["df"].empty:
                disabled = False
    button = st.checkbox("Use log from cache",disabled=disabled)
placeholder = st.empty()

if button and "df" in st.session_state:
    placeholder.success("Using session cached event log.")
else:
    placeholder.empty()
if "df" not in st.session_state.keys(): st.session_state["df"] = None 
df = None
bpmn = None
discovered_xml = None

tab1, tab2 = st.tabs(["Data Frame", "Discovered Process"])

def format_event_log_df(df):
    #df.index.name = "ident:eid"
    df.reset_index(inplace=True)
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"],format="%Y-%m-%d %H:%M:%S,%f")
    return df

if uploaded_file is not None or button: # If an event log is present:

    #Read Event Log
    my_bar.progress(10, text = "Reading event log")
    with tab1:
        if button:
            df = st.session_state["df"].copy()
        if df is None:
            df = pd.read_csv(uploaded_file, index_col=0)
        df = format_event_log_df(df)
        st.subheader("Uploaded Event Log:")
        st.write(df)
        
    #Discovering Process
    my_bar.progress(25, text = "Discover BPMN Process")
    if bpmn is None:
        #df_filtered = pm4py.filter_start_activities(df, ["Process User Request"])
        df_filtered = df#pm4py.filter_variants_by_coverage_percentage(df,0.0)
        bpmn : pm4py.BPMN = pm4py.discover_bpmn_inductive(df_filtered, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    
    #Build Data Disclosed Dataframe
    my_bar.progress(50, text = "Extract tilt:dataDisclosed from event log")
    data_disclosed_df = get_data_disclosed_df(df)

    #Append Data Disclosed to BPMN Element
    my_bar.progress(75, text = "Append tilt:dataDisclosed to BPMN process")
    with tab2:
        discovered_xml = append_tilt_information_to_bpmn(bpmn,data_disclosed_df)
        #st.header("Discovered Process")
        st.info("The process was extended with TILT data disclosed information.")
        st.download_button("Download BPMN Process",data=discovered_xml,file_name="discovered_process.bpmn")
        st.subheader("Process visualization:")
        st.graphviz_chart(bpmnvs.apply(bpmn),use_container_width=True)
    
    #Finished
    my_bar.progress(100, text = "The discovered TILT extended BPMN file is ready.")

if discovered_xml is not None:
    st.info("Download the BPMN file from the 'Discovered Process' tab.")