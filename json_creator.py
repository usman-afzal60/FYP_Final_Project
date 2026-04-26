import json
def create_json_report(data): 
    filename = "/root/pyserver/jsonreports/" + str(data['ID'])+".json"
    with open(filename, "w") as file:
        json.dump(data, file)