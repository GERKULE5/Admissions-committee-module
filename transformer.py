from collections import defaultdict
from parser import parse_all_data

def convert_to_specialty_schema(data_list):
    grouped = defaultdict(list)

    
    for item in data_list:
        code = item.get("code")
        title = item.get("title")
        description = item.get("description", "")

        if not code:
            print('Code is not defined')
            continue
        if not title:
            print('Code is not defined')
            continue
        if not description:
            print('Code is not defined')
            continue
        
        key = (code, title, description)
        grouped[key].append(item)

    result = []

    for (code, title, description), items in grouped.items():
        group_types = []        
        full_years = None       
        not_full_years = None    

        
        for item in items:
            base = item["base"]
            group_type = item["group_type"]

       
            try:
                min_score = float(item["minScore"]) if item["minScore"] else None
            except Exception as e:
                min_score = 0.1
                print(e)

           
            group_spec = {
                "type": group_type,
                "base": base,
                "years": item["duration_years"],
                "places": item["places"],
                "cost": item.get("cost"),
                "minScore": item["minScore"]
            }

           
            group_types.append(group_spec)

          
            if base == "FULL":
                full_years = item["duration_years"]
            elif base == "NOT_FULL":
                not_full_years = item["duration_years"]


        specialty = {
            "title": title,
            "description": description,
            "prefix": None,             
            "code": code,
            # "fullYears": full_years,
            # "notFullYears": not_full_years,
            "groupTypes": group_types
        }

        
        result.append(specialty)

    
    return result