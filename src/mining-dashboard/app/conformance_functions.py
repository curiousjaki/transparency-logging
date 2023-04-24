import xmltodict
import pandas as pd
import uuid

def get_bpmn_element_by_value(d : dict, value, path=(), k="@name"):
    found_element = ({},None)  
    for key, val in d.items():
        if key == k:
            if val == value:
                found_element = d, path
        if type(val) == list:
            for c,i in enumerate(val):
                if type(i)!=dict:
                    continue
                found_element = get_bpmn_element_by_value(i,value,path=path+(key,c,),k=k)
                if found_element != ({},None):
                    break
        elif type(val) == dict:
            found_element = get_bpmn_element_by_value(d[key],value,path=path+(key,),k=k)
        if found_element != ({},None):
            break
    return found_element

def get_list_of_elements_containing_key(d,k,l=[]):
    if k in d.keys():
        l = l +[d]
    else:
        for key, val in d.items():
            if type(val) == list:
                for c,i in enumerate(val):
                    if type(i)!=dict:
                        continue
                    l = get_list_of_elements_containing_key(i,k,l)
            elif type(val) == dict:
                l = get_list_of_elements_containing_key(val,k,l)
    return l

def filter_list_for_element(l=[],key="bpmn:extensionElements", nested_key="tilt:dataDisclosed"):
    new_l = []
    for i in l:
        present_keys = i[key].keys()
        if "@name" not in i.keys(): continue
        for j in present_keys:
            if nested_key in j:
                new_l.append(i)
                break
    return new_l

def extract_data_disclosed_from_element_list(l):
    result = []
    for i in l:
        if "tilt:dataDisclosed" not in i["bpmn:extensionElements"].keys() or "@name" not in i.keys():
            continue
        if type(i["bpmn:extensionElements"]["tilt:dataDisclosed"]) != list:
            i["bpmn:extensionElements"]["tilt:dataDisclosed"] = [i["bpmn:extensionElements"]["tilt:dataDisclosed"]]
        for j in i["bpmn:extensionElements"]["tilt:dataDisclosed"]:
            if "@_id" in j.keys():
                result.append((i["@name"],j["@_id"],))
            else:
                result.append((i["@name"],"",))
    return result

def append_values_to_list(d, key, value_id):
    l = []
    if key in d.keys():
        if type(d[key]) == list:
            for i in d[key]:
                l.append(i[value_id])
        else:
            l.append(d[key][value_id])
    return l

def build_data_disclosed_element(d):
    if type(d) != dict: return
    c = d["@category"] if "@category" in d.keys() else ""
    p = append_values_to_list(d,"tilt:purposes","@purpose")
    l = append_values_to_list(d,"tilt:legalBases","@reference")
    element = {"@category": c,
               "tilt:purposes": p,
               "tilt:legalBases":l}
    if "@_id" not in d.keys():
        print(d)
        d["@_id"] = uuid.uuid5(uuid.NAMESPACE_URL,str(element)) 
    return uuid.uuid5(uuid.NAMESPACE_URL,str(element)),element,d["@_id"]

def get_data_disclosed_dicts(l):
    dicts = []
    for i in l:
        for j in i["bpmn:extensionElements"]["tilt:dataDisclosed"]:
            dicts = dicts + [build_data_disclosed_element(j)]
    return dicts

def build_tilt_element_list(row:pd.Series, column = "tilt:purposes")->list:
    l = []
    if column in row["dict"]:
        for i in row["dict"][column]:
            s = pd.Series(dtype="object")
            s["id"] = row["id"]
            s[column] = i
            l.append(s)
    return l

def build_tilt_element_df(df, tilt_element="tilt:purposes")->pd.DataFrame:
    element_list = df.apply(lambda x: build_tilt_element_list(x,tilt_element),axis=1)
    elements = []
    for e in element_list:
        for i in e:
            elements.append(i)
    return pd.DataFrame(elements).drop_duplicates()



def get_data_disclosed_dfs(discovered_xml,normative_xml):
    discovered_bpmn = xmltodict.parse(discovered_xml)
    normative_bpmn = xmltodict.parse(normative_xml)

    discovered_tilt_bpmn_elements = filter_list_for_element(
        get_list_of_elements_containing_key(discovered_bpmn,"bpmn:extensionElements",[]),
            key="bpmn:extensionElements",
            nested_key="tilt:dataDisclosed")
    normative_tilt_bpmn_elements = filter_list_for_element(
        get_list_of_elements_containing_key(normative_bpmn,"bpmn:extensionElements",[]),
            key="bpmn:extensionElements",
            nested_key="tilt:dataDisclosed")
    
    discovered_data_disclosed_elements = \
        extract_data_disclosed_from_element_list(discovered_tilt_bpmn_elements)
    normative_data_disclosed_elements = \
        extract_data_disclosed_from_element_list(normative_tilt_bpmn_elements)
    
    discovered_new_ids = get_data_disclosed_dicts(discovered_tilt_bpmn_elements)
    normative_new_ids = get_data_disclosed_dicts(normative_tilt_bpmn_elements)

    df_discovered__new = pd.DataFrame(discovered_new_ids,columns=["id_disc","dict","old_id"]).dropna()
    df_discovered_old = pd.DataFrame(discovered_data_disclosed_elements,columns=["name","old_id"]).dropna()
    df_data_disclosed_discovered = pd.merge(df_discovered__new,df_discovered_old,how="outer",on="old_id").drop_duplicates(["id_disc","name","old_id"])

    df_normative_new = pd.DataFrame(normative_new_ids,columns=["id_norm","dict","old_id"]).dropna()
    df_normative_old = pd.DataFrame(normative_data_disclosed_elements,columns=["name","old_id"]).dropna()
    df_data_disclosed_normative = pd.merge(df_normative_new,df_normative_old,how="outer",on="old_id").drop_duplicates(["id_norm","name","old_id"])

    combined_df = pd.concat([df_data_disclosed_discovered.rename(columns={"id_disc":"id"}),df_data_disclosed_normative.rename(columns={"id_norm":"id"})])
    combined_df["category"] = combined_df.apply(lambda x: x["dict"]["@category"],axis=1)
    df_purpsoes = build_tilt_element_df(combined_df,"tilt:purposes")
    df_legal_bases = build_tilt_element_df(combined_df,"tilt:legalBases")
    df_disclosed_delta = pd.merge(df_data_disclosed_discovered[["id_disc","name"]],df_data_disclosed_normative[["id_norm","name"]],how="outer",left_on=["id_disc","name"],right_on=["id_norm","name"])
    df_old_combined = pd.merge(df_data_disclosed_discovered[["id_disc","name"]],df_data_disclosed_normative[["id_norm","name"]],how="outer",left_on=["id_disc","name"],right_on=["id_norm","name"])#.drop_duplicates()
    return combined_df,df_disclosed_delta,df_purpsoes,df_legal_bases,df_data_disclosed_discovered,df_data_disclosed_normative, df_old_combined

def isCompliant(row:pd.Series,df_disclosed_delta)->pd.Series:
    id = str(row['tilt:dataDisclosed:id'])
    df_disclosed_delta["id_norm"] = df_disclosed_delta["id_norm"].apply(lambda x: str(x))
    result = df_disclosed_delta.query(f"id_norm == '{id}' and name == '{row['concept:name']}'")#[df_disclosed_delta["id_norm"] == row["tilt:dataDisclosed:id"]] and df_disclosed_delta["name"]==row["concept:name"]]
    #result = df_disclosed_delta.loc[(df_disclosed_delta["id_norm"]==id)and(df_disclosed_delta["name"]==row["concept:name"])]
    if len(result) <1:
        return False
    else:
        return True
    
def calcualte_percentage_of_compliance(g,column = "tilt:isCompliant",new_colum = "tilt:percentageCompliant"):
    g[new_colum] = g[column].sum()/len(g[column])
    return g
