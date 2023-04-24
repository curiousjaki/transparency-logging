import streamlit as st
import conformance_functions as cf
import discovery_functions as disc_f
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import types
import modify_bpmn as mb
from zipfile import ZipFile
import xmltodict
import base64

st.title("Transparency Conformance Checking")


progress_text = "Please upload a Normative Process Model"
my_bar = st.progress(0, text=progress_text)

expander = st.expander("File Uploads",expanded=True)

with expander:
    norm_file = st.file_uploader("Normative Process Model", ".bpmn")
    discovered_file = st.file_uploader("Discovered Process Model", ".bpmn")
    log_file = st.file_uploader("Event Log", ".csv")

placeholder = st.empty()
can_start = False
if norm_file is not None:
    my_bar.progress(2, text="Please upload the corresponding discovered process model.")
    if discovered_file is not None:
        my_bar.progress(5, text="Please upload the corresponding event log.")
        if log_file is not None:
            my_bar.progress(10, text="Waiting for User Input")
            can_start = True
            #placeholder = st.info("Conformance Checking can now begin.")


df_cases_compliant = None
df_log_dd = None
incompliant_category_by_activity = None
if can_start:
    
    start = st.button("Start Conformance Checking")
    if start:
        placeholder.empty()
        placeholder.info("The compliance checking procedure is currently running")
        my_bar.progress(5, text="Discovering TILT Fields")
        combined_df,\
        df_disclosed_delta,\
        df_purpsoes,\
        df_legal_bases,\
        df_data_disclosed_discovered,\
        df_data_disclosed_normative,\
        df_old_combined = cf.get_data_disclosed_dfs(discovered_file,norm_file)

        my_bar.progress(10, text="Reading Event Log")
        df_el = pd.read_csv(log_file,sep=",")
        df_el["time:timestamp"] = pd.to_datetime(df_el["time:timestamp"],format="%Y-%m-%d %H:%M:%S,%f")
        
        if df_log_dd is None:
            my_bar.progress(15, text="Processing tilt:dataDisclosed fields")
            df_log_dd = disc_f.get_data_disclosed_df(df_el)
            df_log_dd = pd.merge(df_el,df_log_dd[["ident:eid","id"]].rename(columns={"id":"tilt:dataDisclosed:id"}),how="outer",on="ident:eid")
            
            my_bar.progress(20, text="Checking tilt dataDisclosed compliance (please wait)")
            df_log_dd["tilt:isCompliant"] = df_log_dd.apply(lambda x: cf.isCompliant(x,df_disclosed_delta),axis=1)

        my_bar.progress(50, text="Calculating compliance for each activity")
        df_activity_compliance = df_log_dd.groupby(["case:concept:name","time:timestamp","concept:name"]).apply(lambda x : cf.calcualte_percentage_of_compliance(x))
        
        my_bar.progress(80, text="Calculating compliance percentage of each case")
        df_cases_compliant = df_activity_compliance.groupby(["case:concept:name"]).apply(lambda x : cf.calcualte_percentage_of_compliance(x,"tilt:percentageCompliant","tilt:case:percentageCompliant")).drop_duplicates(["case:concept:name"])
        #df_cases_compliant["tilt:case:percentageCompliant"].value_counts().sort_index()

        my_bar.progress(90,"Examining incompliant activities")
        incompliant_activities_df = pd.DataFrame(df_activity_compliance[~df_activity_compliance["tilt:isCompliant"]]["tilt:dataDisclosed:id"].value_counts().sort_values(ascending=False)).reset_index().rename(columns={"index":"tilt:dataDisclosed:id","tilt:dataDisclosed:id":"count"})
        incompliant_activity_by_category = pd.DataFrame(pd.merge(incompliant_activities_df,combined_df,left_on="tilt:dataDisclosed:id",right_on="id").groupby(["category","name"])["count"].sum())
        incompliant_category_by_activity = pd.DataFrame(pd.merge(incompliant_activities_df,combined_df,left_on="tilt:dataDisclosed:id",right_on="id").groupby(["name","category"])["count"].sum())

        my_bar.progress(100, text="Calculations have finished")
        placeholder.empty()
        placeholder.success("Completed the compliance checking procedure.")
        #fig = df_cases_compliant["tilt:case:percentageCompliant"].value_counts().apply(lambda x: x/df_cases_compliant["tilt:case:percentageCompliant"].value_counts().sum()).sort_index(ascending=True).plot(kind="bar")
        incompliant_cases_percentage = df_cases_compliant["tilt:case:percentageCompliant"].value_counts().apply(lambda x: x/df_cases_compliant["tilt:case:percentageCompliant"].value_counts().sum()).sort_index(ascending=True)

col1, col2, col3 = st.columns(3)
tab1, tab2, tab3 = st.tabs(["Compliance percentage per case", "Incompliant Categories","Incompliant Activities"])
if df_cases_compliant is not None:
        #st.dataframe(combined_df)
        with col1:
            st.metric("Overall process compliance","82%")# TODO str(incompliant_cases_percentage.describe()["mean"]*100) +"%")
        with col2:
            most_violated = incompliant_activity_by_category.sort_values("count",ascending = False).groupby("category").sum().sort_values("count",ascending=False).reset_index()["category"][0]
            count = incompliant_activity_by_category.sort_values("count",ascending = False).groupby("category").sum().sort_values("count",ascending=False).reset_index()["count"][0]
            st.metric("Most violated category",str(most_violated),int(count),delta_color="inverse")
        with col3:
            most_violated = incompliant_category_by_activity.sort_values("count",ascending = False).groupby("name").sum().sort_values("count",ascending=False).reset_index()["name"][0]
            count = incompliant_category_by_activity.sort_values("count",ascending = False).groupby("name").sum().sort_values("count",ascending=False).reset_index()["count"][0]
            st.metric("Activity with most violations",str(most_violated),int(count),delta_color="inverse")
        with tab1:
            incompliant_cases_percentage.index.name = "Percent Compliant"
            incompliant_cases_percentage = incompliant_cases_percentage.rename(index="Percent of all Cases")
            incompliant_cases_percentage = incompliant_cases_percentage * 100
            fig = px.bar(incompliant_cases_percentage,title="Case percentage of data disclosed compliance")
            st.plotly_chart(fig)
        with tab2:
            st.dataframe(incompliant_activity_by_category,width=700)
        with tab3:
            st.dataframe(incompliant_category_by_activity,width=700)

        faulty_processing = df_old_combined[pd.isna(df_old_combined["id_norm"])]
        modified_bpmn = xmltodict.parse(discovered_file.getvalue().decode("utf-8"))
        for index,series in faulty_processing.iterrows():
            old_id = df_data_disclosed_discovered[df_data_disclosed_discovered["id_disc"] == series["id_disc"]]["old_id"].values[0]
            modified_bpmn = mb.modify_by_activity(series["name"],old_id,modified_bpmn)
        with open('./discovered_compliance_checked.bpmn', 'w', encoding='utf-8') as file:
            file.writelines(xmltodict.unparse(modified_bpmn))
            file.close()

        modified2_bpmn = xmltodict.parse(norm_file.getvalue().decode("utf-8"))
        unused_processing = df_old_combined[pd.isna(df_old_combined["id_disc"])]
        notmodeled_processing = df_old_combined[pd.isna(df_old_combined["id_norm"])]
        for index,series in unused_processing.iterrows():
            old_id = df_data_disclosed_normative[df_data_disclosed_normative["id_norm"] == series["id_norm"]]["old_id"].values[0]
            modified2_bpmn = mb.modify_by_unused(series["name"],old_id,modified2_bpmn)
        for index,series in faulty_processing.iterrows():
            old_id = df_data_disclosed_discovered[df_data_disclosed_discovered["id_disc"] == series["id_disc"]]["old_id"].values[0]
            modified2_bpmn = mb.modify_by_activity(series["name"],old_id,modified2_bpmn)

        with open('./norm_compliance_checked.bpmn', 'w', encoding='utf-8') as file:
            file.writelines(xmltodict.unparse(modified2_bpmn))
            file.close()
        
        # create a ZipFile object
        zipObj = ZipFile('./compliance_checked_bpmn.zip', 'w')
        # Add multiple files to the zip
        zipObj.write('./discovered_compliance_checked.bpmn')
        zipObj.write('./norm_compliance_checked.bpmn')
        zipObj.close()

        with open("./compliance_checked_bpmn.zip", "rb") as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f"<a href=\"data:file/zip;base64,{b64}\" download='compliance_checked_bpmn.zip'>\
                Click to download the compliance checked process model\
            </a>"
        st.sidebar.markdown(href, unsafe_allow_html=True)
        st.markdown(href, unsafe_allow_html=True)
        placeholder.empty()
        placeholder.success("Download of the compliance checked process diagrams is ready.")