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

def modify_by_unused(activity,old_id,bpmn):
    error_element, *n = get_bpmn_element_by_value(bpmn,activity)
    error_data_disclosed, *n = get_bpmn_element_by_value(error_element,old_id,k="@_id")
    if error_data_disclosed =={}:
        return bpmn
    if "UNUSED:" not in error_data_disclosed["@category"]:
        error_data_disclosed["@category"] = "UNUSED:"+error_data_disclosed["@category"]
    element_id = error_element["@id"]
    shape, *n= get_bpmn_element_by_value(bpmn,element_id,k="@bpmnElement")
    shape["@bioc:stroke"] ="#FFFF00"
    #shape["@bioc:fill"]="#8728E3"
    #shape["@color:background-color"]="#ffe0b2"
    shape["@color:border-color"]="#FFFF00"
    return bpmn


def modify_by_activity(activity,old_id,bpmn,other_bpmn=None):
    error_element, *n = get_bpmn_element_by_value(bpmn,activity)
    if error_element == {}:
        return bpmn
        append_to_element_by_type(bpmn,"bpmn:process","bpmn:task",{"@id":"Activity_"+activity.replace(" ","_"),"@name":activity})
        error_element, *n = get_bpmn_element_by_value(bpmn,activity)
    error_data_disclosed, *n = get_bpmn_element_by_value(error_element,old_id,k="@_id")
    element_id = error_element["@id"]
    shape, *n= get_bpmn_element_by_value(bpmn,element_id,k="@bpmnElement")
    #shape["@bioc:stroke"] ="#000000"
    shape["@bioc:fill"]="#BD523E"
    shape["@color:background-color"]="#BD523E"
    #shape["@color:border-color"]="#BD523E"
    if error_data_disclosed == {}:
        #TODO Falls das Data Disclosed Feld nicht im Diagramm existiert, dann muss es hinzugefügt werden....
        #error_data_disclosed, *n = get_bpmn_element_by_value()
        #print(activity,error_element,old_id)
        return bpmn
    if "UNCOMPLIANT:" not in error_data_disclosed["@category"]:
        error_data_disclosed["@category"] = "UNCOMPLIANT:"+error_data_disclosed["@category"]
    return bpmn

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
    return str(hash(str(element))),element,d["@_id"]


def get_bpmn_element_by_type(d:dict,t)->list:
    if t in d.keys():
        return[d[t]]
    found_elements = []
    for key, val in d.items():
        if type(val) == dict:
            rec = get_bpmn_element_by_type(val,t)
            if rec:
                found_elements = found_elements + rec
            continue
        if val is None:
            continue
        for v in val:
            if v == t:
                found_elements = found_elements + found_elements + d[key][t]
            elif type(v) == list:
                for i in v:
                    if type(i) == dict:
                        rec = get_bpmn_element_by_type(i,t)
                        if rec:
                            found_elements = found_elements + rec
            elif type(v)==dict:
                rec = get_bpmn_element_by_type(v,t)
                if rec:
                    found_elements = found_elements + rec
    return found_elements if len(found_elements) > 0 else None

def append_to_element_by_type(d:dict,t,key,new_element)->dict:
    found_elements = get_bpmn_element_by_type(d,t)
    found_element = found_elements[0]#[0]
    if t != "bpmndi:BPMNPlane":
        found_shapes = get_bpmn_element_by_type(d,"bpmndi:BPMNPlane")
        #found_shapes[0]["bpmndi:BPMNShape"].append({'@id': new_element["@id"]+"_di",
        #        '@bpmnElement': new_element["@id"],
        #        'dc:Bounds': {'@x': '100', '@y': '100', '@width': '100', '@height': '80'},
        #        'bpmndi:BPMNLabel': None})
        print(found_element)
    #found_element[key] = new_element
    return d