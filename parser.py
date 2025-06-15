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
from bs4 import BeautifulSoup
import re


def parse_description(code: str):
    formatted_code = code.replace('.', '-')
    description_url = f"http://www.nke.ru/applicants/directions_specialty_exams/{formatted_code}.php"

    try:
        description_response = requests.get(description_url)
        if description_response.status_code != 200:
            return ["Description not found"]

        description_soup = BeautifulSoup(description_response.text, 'html.parser')
        description_content = description_soup.find('div', class_="white-box col-margin-bottom padding-box")

        if not description_content:
            return ["Description not found"]

        description_text = description_content.find_all('p')
        description = []
        for p in description_text:
            text = p.get_text(strip=True)
            if "численность" in text.lower() or "основная" in text.lower():
                break
            description.append(text)
        return description
    except Exception as e:
        return ["Parsing error"]


def parse_cost_of_training_intramural(html_text=None):

    url_cost = 'http://nke.ru/applicants/cost_of_training/'
    if html_text is None:
        response = requests.get(url_cost)
        if response.status_code != 200:
            raise Exception(f'{response.status_code}')
        html_text = response.text

    soup = BeautifulSoup(html_text, 'html.parser')
    tables = soup.find_all('table')

    if len(tables) < 1:
        raise Exception("nothing tables")

    cost_table = tables[0]
    t_body = cost_table.find('tbody') or cost_table
    rows = t_body.find_all('tr')[1:]

    costs_data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        code_name = cells[0].get_text(strip=True)
        code = code_name[:8]
        try:
            cost = cells[2].get_text(strip=True)
            cost_value = int(cost.replace(" ", "").replace("\u2009", ""))
        except (ValueError, IndexError):
            continue
        costs_data[code] = cost_value

    return costs_data


def parse_cost_of_training_extramural(html_text=None):

    url_cost = 'http://nke.ru/applicants/cost_of_training/'
    if html_text is None:
        response = requests.get(url_cost)
        if response.status_code != 200:
            raise Exception(f'Page cost of training not found: {response.status_code}')
        html_text = response.text

    soup = BeautifulSoup(html_text, 'html.parser')
    tables = soup.find_all('table')

    if len(tables) < 2:
        raise Exception("less than 2 tables")

    cost_table = tables[1]
    t_body = cost_table.find('tbody') or cost_table
    rows = t_body.find_all('tr')[1:]

    extramural_costs_data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        code_name = cells[0].get_text(strip=True)
        code = code_name[:8]
        try:
            cost = cells[2].get_text(strip=True)
            cost_value = int(cost.replace(" ", "").replace("\u2009", ""))
        except (ValueError, IndexError):
            continue
        extramural_costs_data[code] = cost_value

    return extramural_costs_data


def parse_table_intramural(table, base, costs_data):

    rows = table.find_all('tr')[1:]
    table_data = []

    for row in rows:
        cells = row.find_all('td')
        if not cells or len(cells) < 3:
            continue

        values = [cell.get_text(strip=True) for cell in cells]

        code_name = values[0]
        code = code_name[:8]
        name = code_name[8:].lstrip()
        description = parse_description(code)

        duration_str = values[2] if len(values) > 2 else ""
        match = re.search(r'(\d+)г\.', duration_str)
        years = int(match.group(1)) if match else 0

        budget_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        paid_places = int(values[4]) if len(values) > 4 and values[4].isdigit() else 0
        min_score = 4.56

        if budget_places > 0:
            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "FREE",
                'duration_years': years + 1,
                'places': budget_places,
                'min_score': min_score
            }
            table_data.append(item)

        if paid_places > 0:
            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "COMMERCIAL",
                'duration_years': years + 1,
                'places': paid_places,
                'cost': costs_data.get(code),
                'min_score': min_score
            }
            table_data.append(item)

    return table_data


def parse_extramural_table(table, extramural_costs_data):

    rows = table.find_all('tr')[1:]
    extramural_table_data = []

    for row in rows:
        cells = row.find_all('td')
        if not cells or len(cells) < 3:
            continue

        values = [cell.get_text(strip=True) for cell in cells]

        code_name = values[0]
        code = code_name[:8]
        name = code_name[9:]
        description = parse_description(code)

        academic_base = values[1]
        if "9" in academic_base.lower():
            base = "NOT_FULL"
        elif "11" in academic_base.lower():
            base = "FULL"
        

        duration_str = values[2] if len(values) > 2 else ""
        match = re.search(r'(\d+)г\.', duration_str)
        years = int(match.group(1)) if match else 0

        paid_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        min_score = 4.55

        if paid_places > 0:
            item = {
                'code': code,
                'name': name,
                'description': description,
                'base': base,
                'group_type': "EXTRAMURAL",
                'duration_years': years + 1,
                'places': paid_places,
                'cost': extramural_costs_data.get(code),
                'min_score': min_score
            }
            extramural_table_data.append(item)

    return extramural_table_data


def parse_rating():

    rating_url = 'http://nke.ru/applicants/the_admissions_committee/reyting-abiturientov.php'

    try:
        rating_response = requests.get(rating_url)
        if rating_response.status_code != 200:
            raise Exception(f"Не удалось открыть рейтинг: {rating_response.status_code}")

        rating_soup = BeautifulSoup(rating_response.text, 'html.parser')
        rating_main_table = rating_soup.find('table')
        rating_tbody = rating_main_table.find('tbody')
        rows = rating_tbody.find_all('tr')[1:]
        rating_table_data = []

        current_base = 'None'
        current_qualification = 'None'

        for row in rows:
            cells = row.find_all('td')
            values = []

            for cell in cells:
                cell_text = cell.get_text(strip=True)
                if cell_text.lower() == 'на базе 9кл., специальности спо':
                    current_base = 'NOT_FULL'
                    current_qualification = 'SPECIALTY'
                    continue
                elif cell_text.lower() == 'на базе 11кл., специальности спо':
                    current_base = 'FULL'
                    current_qualification = 'SPECIALTY'
                    continue
                elif cell_text.lower() == 'на базе 9кл., профессия':
                    current_base = 'NOT_FULL'
                    current_qualification = 'PROFESSION'
                    continue

                if cell_text:
                    values.append(cell_text)

            if len(values) < 1:
                continue

            code_name = values[0]
            code = code_name[:8]
            name = code_name[8:].lstrip()

            plan = int(values[1]) if len(values) > 1 and values[1].isdigit() else 0
            statement_quantity = int(values[2]) if len(values) > 2 and values[2].isdigit() else 0
            competition = float(values[3]) if len(values) > 3 else 0.0

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
    except Exception as e:
        print(f"Parsing rating error: {e}")
        return []


def parse_educational_loan():

    loan_url = 'http://nke.ru/applicants/educational-loan/the-project/'

    try:
        loan_response = requests.get(loan_url)
        if loan_response.status_code != 200:
            raise Exception(f"Не удалось открыть страницу с кредитом: {loan_response.status_code}")

        loan_soup = BeautifulSoup(loan_response.text, 'html.parser')
        loan_content = loan_soup.find('div', class_='white-box col-margin-bottom padding-box')

        loan_content_data = []
        if loan_content:
            for p in loan_content.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    loan_content_data.append(text)

        return loan_content_data
    except Exception as e:
        print(f"Parsing loan error: {e}")
        return []


def parse_all_data():

    url = 'http://www.nke.ru/applicants/directions_specialty_exams/'

    try:
       
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Page not found: {response.status_code}")

 
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        if len(tables) < 3:
            raise Exception("Less than 3 tables")

        intramural_not_full_table = tables[0]
        intramural_full_table = tables[1]
        extramural_table = tables[2]

     
        # costs_data = parse_cost_of_training_intramural()
        # extramural_costs_data = parse_cost_of_training_extramural()

        data1 = parse_table_intramural(intramural_not_full_table, base="NOT_FULL", costs_data=parse_cost_of_training_intramural())
        data2 = parse_table_intramural(intramural_full_table, base="FULL", costs_data=0)
        data3 = parse_extramural_table(extramural_table, extramural_costs_data=parse_cost_of_training_extramural())

        return data1 + data2 + data3

    except Exception as e:
        print(f"Parsing Error: {e}")
        return []



