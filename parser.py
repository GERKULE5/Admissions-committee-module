# # Код специальности
# # Название
# # описание
# # База 
# # export enum AcademicBase {
# #   FULL = 'FULL',
# #   NOT_FULL = 'NOT_FULL',
# # }
# # Бюджет/коммериця/заочное
# # export enum GroupType {
# #   FREE = 'FREE',
# #   COMMERCIAL = 'COMMERCIAL',
# #  EXTRAMURAL = 'EXTRAMURAL',

# # }

# # Срок (полных лет)
# # Кол-во бюджетных мест
# # Кол-во платных мест
# # Кол-во свободных мест
# # Стоимость
# # Минимальный проходной балл


import requests
import re
from bs4 import BeautifulSoup


def parse_description(code: str):

    formatted_code = code.replace('.', '-')

    description_url = f"http://www.nke.ru/applicants/directions_specialty_exams/{formatted_code}.php"
    try:
        description_response = requests.get(description_url)

        if description_response.status_code !=200:
            return "Description not found1"
        
        description_soup = BeautifulSoup(description_response.text, 'html.parser')

        description_content = description_soup.find('div', class_="white-box col-margin-bottom padding-box")

        if description_content:
            description_text = description_content.find_all('p')
            description = []

            for p in description_text:
                    text = p.get_text(strip=True)

                    if "численность" in text.lower():
                        
                        break

                    if 'основная' in text.lower():
                        break
                    description.append(text)
            return description
        else:
            return "Description not found2"

    except Exception as e:
        print(f"Parsing error {url}: {e}")
        return "Description not found3"


url_cost = 'http://nke.ru/applicants/cost_of_training/'

response_cost = requests.get(url_cost)

# COST INTRAMURAL PARSE FUNCTION
def parse_cost_of_training_intramural():
    
    if response_cost.status_code != 200:
        raise Exception(f'Failed to load {response_cost.status_code}')

    soup_of_cost = BeautifulSoup(response_cost.text, 'html.parser')

    tables_of_cost = soup_of_cost.find_all('table')
    cost_table = tables_of_cost[0]
    t_body = cost_table.find('tbody') or tables_of_cost
    rows = t_body.find_all('tr')[1:]

    costs_data = {}

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        code_name = cells[0].get_text(strip=True)
        code = code_name[:8]
        name = code_name[8:]
        cost = cells[2].get_text(strip=True)

        try:
            cost_value = int(cost.replace(" ", "").replace("\u2009", ""))
        except ValueError:
            continue

        costs_data[code] = cost_value

    return costs_data

# COST EXTRAMURAL PARSE FUNCTION
def parse_cost_of_training_extramural():
    
    if response_cost.status_code != 200:
        raise Exception(f'Failed to load {response_cost.status_code}')

    soup_of_cost = BeautifulSoup(response_cost.text, 'html.parser')

    tables_of_cost = soup_of_cost.find_all('table')
    cost_table = tables_of_cost[1]
    t_body = cost_table.find('tbody') or tables_of_cost
    rows = t_body.find_all('tr')[1:]

    extramural_costs_data = {}

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        code_name = cells[0].get_text(strip=True)
        code = code_name[:8]
        name = code_name[8:]
        cost = cells[2].get_text(strip=True)

        try:
            cost_value = int(cost.replace(" ", "").replace("\u2009", ""))
        except ValueError:
            continue

        extramural_costs_data[code] = cost_value

    return extramural_costs_data


url = 'http://www.nke.ru/applicants/directions_specialty_exams/'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f'Failed to load {response.status_code}')

soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table')

intramural_not_full_table = tables[0]  # Очная, NOT_FULL
intramural_full_table = tables[1]      # Очная, FULL
extramural_table = tables[2]           # заочная

# TABLE INTRAMURAL PARSE FUNCTION
def parse_table_intramural(table, base, costs_data):
    rows = table.find_all('tr')[1:]  
    table_data = []

    for row in rows:
        cells = row.find_all('td')
        if not cells or len(cells) < 3:
            continue  

        values = [cell.get_text(strip=True) for cell in cells]

        if not values or not values[0]:
            continue

        
        code_name = values[0]
        code = code_name[:8]
        name = code_name[8:].lstrip()
        description = parse_description(code) 

        # срок обучения
        duration_str = values[2] if len(values) > 2 else ""
        match = re.search(r'(\d+)г\.', duration_str)
        years = int(match.group(1)) if match else 0

        budget_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        paid_places = int(values[4]) if len(values) > 4 and values[4].isdigit() else 0
        min_score = 4.55

        if budget_places >0:

            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "FREE",
                'duration_years': years+1,
                'places': budget_places,
                'min_score': min_score
            }
            table_data.append(item)
            
        if paid_places> 0:
            
            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "COMMERCIAL",
                'duration_years': years+1,
                'places': paid_places,
                'cost': costs_data.get(code),
                'min_score': min_score
            }
            table_data.append(item)
            
    return table_data

data1 = parse_table_intramural(intramural_not_full_table, base="NOT_FULL", costs_data=parse_cost_of_training_intramural())
data2 = parse_table_intramural(intramural_full_table, base="FULL", costs_data=0)

# TABLE EXTRAMURAL PARSE FUNCTION
def parse_extramural_table(table, extramular_costs_data):
    rows = table.find_all('tr')[1:]  
    extramural_table_data = []
    
    for row in rows:
        cells = row.find_all('td')
        if not cells or len(cells) < 3:
            continue  

        values = [cell.get_text(strip=True) for cell in cells]

        if not values or not values[0]:
            continue

        code_name = values[0]
        code = code_name[:8]
        name = code_name[9:]
        description = parse_description(code) 
        academic_base = values[1] if len(values) > 1 else None
        if "9" in values[1].lower():
            base = "NOT_FULL"
        if "11" in values[1].lower():
            base = "FULL"

        # срок обучения
        duration_str = values[2] if len(values) > 2 else ""
        match = re.search(r'(\d+)г\.', duration_str)
        years = int(match.group(1)) if match else 0

        # budget_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        paid_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        min_score = 4.55

        if paid_places>0:
            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "EXTRAMURAL",
                'duration_years': years+1,
                'places': paid_places,
                'cost': extramular_costs_data.get(code),
                'min_score': min_score
            }
            extramural_table_data.append(item)
    return extramural_table_data
data3 = parse_extramural_table(extramural_table, extramular_costs_data=parse_cost_of_training_extramural())

all_data = data1 + data2 + data3

def parse_rating():
    rating_table_data = []
    current_base = 'None'
    current_qualification = 'None'

    rating_url = 'http://nke.ru/applicants/the_admissions_committee/reyting-abiturientov.php'
    rating_response = requests.get(rating_url)
    rating_soup = BeautifulSoup(rating_response.text, 'html.parser')

    rating_main_table = rating_soup.find('table')
    rating_tbody = rating_main_table.find('tbody')
    rows = rating_tbody.find_all('tr')[1:]

    for row in rows:
        cells = row.find_all('td')
        values = []
        for cell in cells:
            
            if cell.get_text(strip=True).lower() == 'на базе 9кл., специальности спо':
                current_base = 'NOT_FULL'
                current_qualification = 'SPECIALTY'
                continue
                
            if cell.get_text(strip=True).lower() == 'на базе 11кл., специальности спо':
                current_base = 'FULL'
                current_qualification = 'SPECIALTY'
                continue

            if cell.get_text(strip=True).lower() == 'на базе 9кл., профессия':
                current_base = 'NOT_FULL'
                current_qualification = 'PROFESSION'
                continue
            
            values.append(cell.get_text(strip=True))

        if len(values)<1:
            continue
        
        code_name = values[0]
        code = code_name[:8]
        name = code_name[8:].lstrip()
        plan = int(values[1])
        statement_quantity = int(values[2])
        competition = float(values[3])

        item = {
            'code': code,
            'name': name,
            'plan': plan,
            'statement_quantity': statement_quantity,
            'competition': competition,
            'base': current_base,
            'skill': current_qualification
        }
        rating_table_data.append(item)
    return rating_table_data
    
rating_data = parse_rating()
print(rating_data)


            
        





# print('-----------------------------------------NOT FULL-----------------------------------')
# for item in data1:
#     print(f'{item}\n')
# print('-----------------------------------------FULL-----------------------------------')
# for item in data2:
#     print(f'{item}\n')

# print('-----------------------------------------EXTRAMURAL-----------------------------------')
# for item in data3:
#     print(f'{item}\n')
# result = parse_cost_of_training_intramural()
# print(result)
# result2 = parse_cost_of_training_extramural()
# print(result2)