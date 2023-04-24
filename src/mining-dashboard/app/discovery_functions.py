import json
import pandas as pd
import xml.etree.ElementTree as ET
import pm4py
import uuid

def convert_to_sorted_list(s:str):
    if type(s) != str:return s
    l = json.loads(s.replace("\'","\""))
    if type(l)==list: l.sort()
    return l

def generate_data_disclosed_uuid(s:pd.Series,id_key="@_id",category_key="@category",legal_bases_key="tilt:legalBases",purposes_key="tilt:purposes")->dict:
    legal_bases = convert_to_sorted_list(s["tilt:legal_bases"])
    purposes = convert_to_sorted_list(s["tilt:purposes"])
    element={
        category_key:s["tilt:data_disclosed"],
        purposes_key:purposes,
        legal_bases_key:legal_bases
    }
    return uuid.uuid5(uuid.NAMESPACE_URL,str(element))

def build_data_disclosed_element(s:pd.Series)->dict:
    legal_bases = [{"reference": i ,"description":None} for i in convert_to_sorted_list(s["tilt:legal_bases"])]
    purposes = [{"purpose": i ,"description":None} for i in convert_to_sorted_list(s["tilt:purposes"])]
    return {
        "_id":s["id"],
        "category":s["tilt:data_disclosed"],
        "legalBases":legal_bases,
        "purposes":purposes
    }

def get_data_disclosed_df(df):
    tilt_columns = [tilt_column for tilt_column in df.columns if tilt_column.startswith("tilt:")]
    for c in tilt_columns:
        df[c] = df[c].apply(convert_to_sorted_list)
    dd_df = df[["ident:eid","concept:name"]+tilt_columns]
    for c in [c for c in tilt_columns if c != "tilt:data_disclosed"]:
        dd_df[c] = dd_df[c].apply(lambda x: str(x))
    dd_df = dd_df.set_index(["ident:eid","concept:name"]+[c for c in tilt_columns if c != "tilt:data_disclosed"])
    dd_df = dd_df.apply(lambda x: pd.Series(x).explode()).reset_index()
    dd_df["id"] = dd_df[tilt_columns].apply(generate_data_disclosed_uuid,axis=1)
    unique_dd = dd_df.drop_duplicates(subset="id")
    unique_dd["tilt:element"] = unique_dd.apply(build_data_disclosed_element,axis=1)
    return pd.merge(left=dd_df,right=unique_dd[["id","tilt:element"]], on="id")

def append_tilt_information_to_bpmn(bpmn,df):
    ns = {
    "bpmn":"http://www.omg.org/spec/BPMN/20100524/MODEL",
    "tilt":"mytilturi.com"}
    ET.register_namespace("tilt","mytiltURI.com")
    ET.register_namespace("bpmn","http://www.omg.org/spec/BPMN/20100524/MODEL")
    ET.register_namespace("bpmndi","http://www.omg.org/spec/BPMN/20100524/DI")
    ET.register_namespace("omgdc","http://www.omg.org/spec/DD/20100524/DC")
    ET.register_namespace("omgdi","http://www.omg.org/spec/DD/20100524/DI")
    ET.register_namespace("xsi","http://www.w3.org/2001/XMLSchema-instance")
    ET.register_namespace("xsd","http://www.w3.org/2001/XMLSchema")

    pm4py.write_bpmn(bpmn,"/tmp/temp.bpmn")
    tree = ET.parse("/tmp/temp.bpmn")
    root = tree.getroot()

    for task in root.find("bpmn:process",ns).findall("bpmn:task",ns):
        extensionElements = ET.SubElement(task,"bpmn:extensionElements")
        concept_name = task.attrib["name"]
        relevant_df = df[df["concept:name"]==concept_name].drop_duplicates("id")
        for id in relevant_df["id"].value_counts().index:
            elements = relevant_df[relevant_df["id"]==id]["tilt:element"].values
            if len(elements) != 0:
                dataElement = elements[0]
            else:
                continue
            dataDisclosed = ET.SubElement(extensionElements,"tilt:dataDisclosed")
            dataDisclosed.attrib["_id"] = str(id)
            dataDisclosed.attrib["category"] = dataElement["category"]
            for x in dataElement["legalBases"]:
                lb = ET.SubElement(dataDisclosed,"tilt:legalBases")
                lb.attrib["reference"] = x["reference"]
            for x in dataElement["purposes"]:
                lb = ET.SubElement(dataDisclosed,"tilt:purposes")
                lb.attrib["purpose"] = x["purpose"]
    tree.write("/tmp/temp_with_tilt.bpmn")
    with open("/tmp/temp_with_tilt.bpmn") as f:
        xml = f.read()
        f.close()
    return xml