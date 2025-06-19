from collections import defaultdict
from parser import parse_all_data

def convert_to_specialty_schema(data_list):
    grouped = defaultdict(list)

    
    for item in data_list:
       
        key = (item['code'], item['title'], item['description'])
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
                min_score = float(item["minScore"]) if item["minScore"] and item["minScore"].isdigit() else None
            except Exception:
                min_score = None

           
            group_spec = {
                "type": group_type,
                "base": base,
                "years": item["duration_years"],
                "places": item["places"],
                "cost": item.get("cost"),
                "minScore": min_score
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

