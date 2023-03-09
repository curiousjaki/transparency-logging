#from tilt import tilt
class Pellucid:
    def __init__(self, activities = {}):
        self.activities : dict = activities # cant be events as events are identified by their case:concept:name id

        #TODO: Build data disclosed Lib
    

    def  _call_(self):
        raise NotImplementedError()
    

    def get_activity_key(self,concept_name):
        return next((key for (key,item) in self.activities.items() if item["concept_name"] == concept_name),None)
    

    def create_activity(self,concept_name) -> None:
        key = self.get_activity_key(concept_name=concept_name)
        if key == None:
            self.activities[list(self.activities.keys())+1 if len(list(self.activities.keys()))!=0 else 0] = {"concept_name":concept_name,"data_disclosed":{}}
        else:
            raise KeyError("This activity already exists.")
        

    def get_data_disclosed(self,activity_key,):
        return
    
    def add_to_activity(self,activity_key):
        pass

p = Pellucid()
print(p)