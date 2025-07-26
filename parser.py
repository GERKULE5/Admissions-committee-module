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
import logging
from openai import OpenAI
from io import BytesIO
import json
import os
import pdfplumber
import markdown


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s"
)

minScore_data = None

def parse_description(code: str): #

    logger.debug(f"Starting description parsing for code : {code}")

    formatted_code = code.replace('.', '-')
    description_url = f"http://www.nke.ru/applicants/directions_specialty_exams/{formatted_code}.php"
    

    try:
        
        description_response = requests.get(description_url)
        if description_response.status_code != 200:
            logger.warning(f"Failed url: status code: {description_response.status_code}")
            return 'Description not found'

        

        description_soup = BeautifulSoup(description_response.text, 'html.parser')
        description_content = description_soup.find('div', class_="white-box col-margin-bottom padding-box")

        if not description_content:
            logger.warning("Description block not found")
            return None

        description_title = description_content.find_all('h1')
        description_text = description_content.find_all('p')
        description = []
        for h in description_title:
            title = h.get_text(strip=True)
            description.append(f'# {title}')
        for p in description_text:
            text = p.get_text(strip=True)
            if "численность" in text.lower() or "основная" in text.lower():
                break
            
            description.append(text)
            description_str = description
        if not description_str:
            logger.warning("Empty description after parsing")
            return None
        description_content_md = description_md(description)
        
        logger.debug(f"Successfully parsed description for code {code}")
        return description_content_md
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while parsing description for {code}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.critical(f"Critical error while parsing description for {code}: {e}", exc_info=True)
        return None


def description_md(paragraphs):
    markdown_lines = []
    i = 0
    while i<len(paragraphs):
        line = paragraphs[i]
        if len(line)<100 and (line.endswith('?') or line.endswith(':')):
            markdown_lines.append(f'### {line}')
            i+=1
        elif "чему научат?" in line.lower():
            markdown_lines.append('')
            while i < len(paragraphs) and (paragraphs[i].startswith('•')):
                item = paragraphs[i].lstrip('-').strip()
                markdown_lines.append(f'- {item}')
                i+=1
            markdown_lines.append('')
        
        else:
            markdown_lines.append(line)
            i+=1

    return '\n'.join(markdown_lines)


def parse_cost_of_training_intramural(html_text=None): #


    logger.debug("Starting Cost of training (INTRAMURAL) parsing")
    url_cost = 'http://nke.ru/applicants/cost_of_training/'

    try:

        if html_text is None:
            response = requests.get(url_cost)
            if response.status_code != 200:
                logger.warning(f'Page cost of training (INTRAMURAL) not found: {response.status_code}')
                raise Exception(f'{response.status_code}')
            html_text = response.text

        soup = BeautifulSoup(html_text, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) < 1:
            logger.warning("nothing tables")
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
                logger.warning(f'Cost of training (INTRAMURAL) {code}: {e}')
                continue
            costs_data[code] = cost_value
        logger.debug("Successfully parsed Cost of training (INTRAMURAL)")
        return costs_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while parsing Cost of training (INTRAMURAL): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.critical(f"Critical error while parsing Cost of training (INTRAMURAL) for {code}: {e}", exc_info=True)
        return None
    

def parse_cost_of_training_extramural(html_text=None): #

    logger.debug("Starting Cost of training (EXTRAMURAL) parsing")
    url_cost = 'http://nke.ru/applicants/cost_of_training/'

    try:

        if html_text is None:
            response = requests.get(url_cost)
            if response.status_code != 200:
                logger.warning(f'Page cost of training (EXTRAMURAL) not found: {response.status_code}')
            html_text = response.text

        soup = BeautifulSoup(html_text, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) < 2:
            logger.warning("less than 2 tables")

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
                logger.warning(f'Cost of training (EXTRAMURAL) {code}: {e}')
                continue

            extramural_costs_data[code] = cost_value
        logger.debug("Successfully parsed Cost of training (EXTRAMURAL)")
        return extramural_costs_data
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while parsing Cost of training (EXTRAMURAL): {e}", exc_info=True)
        return None
    except Exception as e:
        logger.critical(f"Critical error while parsing Cost of training (EXTRAMURAL): {e}", exc_info=True)
        return None

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

PROMPT_TEMPLATE = """
Ты помощник, который преобразует данные из текста в структурированный JSON формат.

На входе ты получаешь текст со средними баллами для специальностей специальностей.

Твоя задача вернуть JSON-файл по схеме:

title: str
code: str
base: str
groupType: str
notTrueMinScore: float
minScore: float

Список словарей назови minScores


Также title должен быть измеенён следующим образом и добавлен code 8(символов):

"Информационные системы и программирование" = "09.02.07", "Информационные системы и программирование"
"Сетевое и системное администрирование" = "09.02.06", "Сетевое и системное администрирование"
"Компьютерные системы и комплексы" = "09.02.01", "Компьютерные системы и комплексы"
"Монтаж, ТО и ремонт ЭП" = "11.02.16", "Монтаж, техническое обслуживание и ремонт электронных приборов и устройств"
"Оператор ИСиР" = "09.01.03", "Оператор информационных систем и ресурсов"
"Обеспечение ИБ АС" = "10.02.05", "Обеспечение информационной безопасности автоматизированных систем"

Документ поделен на несколько блоков:

1. ЗА СЧЕТ БЮДЖЕТНЫХ АССИГНОВАНИЙ НСО(groupType = 'FREE')
2. ПО ДОГОВОРАМ ОПЛАТЫ ЗА СЧЕТ СРЕДСТВ ФИЗИЧЕСКИХ И/ИЛИ ЮРИДИЧЕСКИХ ЛИЦ(groupType = 'COMMERCIAL, notTrueMinScore = null)


Пример:

ЗА СЧЕТ БЮДЖЕТНЫХ АССИГНОВАНИЙ НСО
Информационные системы
и программирование
(9 класс)
- 4,7 - 4,368

1. Название специальности(title: "Информационные системы и программирование")
2. Академическая база в скобках после названия специальности (если 9 класс, то base: "NOT_FULL) или (если 11 класс, то base: "FULL")
3. Средний балл по копиям и оригиналам аттестатов(если стоит больше 2 дефиса то notTrueMinScore: null)
4. Средний балл только по оригиналам(если стоит больше 2 дефиса то minScore: null)

Вот JSON-структура для примера:

title: "Информационные системы и программирование"
code: "09.02.07"
base: "NOT_FULL"
groupType: "FREE"
notTrureMinScore: 4.7
minScore: 4.368

{text}
"""


def parse_min_score_ai(): #
    """
    Парсит PDF, отправляет текст модели,
    получает JSON и возвращает список minScores.
    """
    global minScore_data
    logger.debug("Starting minScore ai parsing")

    url_score = 'http://nke.ru/applicants/the_admissions_committee/top/m-p-s.pdf'

    try:
        response = requests.get(url_score)
        if response.status_code != 200:
            raise Exception(f"Failed to load PDF: {response.status_code}")

        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = ""
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"

        prompt = PROMPT_TEMPLATE.format(text=text)

        model_name = os.getenv("MODEL", "mistralai/mistral-7b-instruct:free")  # Резервная модель

        response_ai = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты помощник, который преобразует данные из текста в структурированный JSON формат"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )

        raw_content = response_ai.choices[0].message.content.strip()
        
        
        logger.debug(f"Raw model response:\n{raw_content}")

        try:
            parsed_data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error(f"Parsing error JSON: {e}")
            logger.debug(f"Incorrect JSON:\n{raw_content}")
            return []

        if isinstance(parsed_data, dict) and "minScores" in parsed_data:
            minScore_data = parsed_data["minScores"]
        elif isinstance(parsed_data, list):
            minScore_data = parsed_data
        else:
            logger.warning("Model returned unknown structure")
            minScore_data = []

        return minScore_data

    except Exception as e:
        logger.critical(f"Critical error while parsing minScore ai: {e}", exc_info=True)
        return []


def get_all_minScores(): #
    global minScore_data

    if minScore_data is None:
        minScore_data = parse_min_score_ai()

    if not isinstance(minScore_data, list):
        logger.warning("minScore_data is not a list")
        minScore_data = []

    return minScore_data


def find_minScore(code, base, groupType): #
    logger.debug(f"Finding minScore for: {code}, {base}, {groupType}")

    data = get_all_minScores()

    if not data:
        logger.warning("minScore data is not loaded or empty")
        return None

    for entry in data:
        if not isinstance(entry, dict):
            logger.warning(f"Wrong format of element: {entry}")
            continue

        if (
            entry.get("code") == code and
            entry.get("base") == base and
            entry.get("groupType") == groupType
        ):
            min_score = entry.get("minScore")
            logger.info(f"Successfully found minScore: {min_score} for {code}, {base}, {groupType}")
            return float(min_score) if min_score not in (None, '') else None

    logger.warning(f"Not found minScore for {code}, {base}, {groupType}")
    return None


def parse_table_intramural(table, base, costs_data):

    id = None
    rows = table.find_all('tr')[1:]
    table_data = []

    for row in rows:
        cells = row.find_all('td')
        if not cells or len(cells) < 3:
            continue

        values = [cell.get_text(strip=True) for cell in cells]

        code_name = values[0]
        code = code_name[:8]
        title = code_name[8:].lstrip()
        description = parse_description(code)
        # academicBase = base
        duration_str = values[2] if len(values) > 2 else ""
        match = re.search(r'(\d+)г\.', duration_str)
        years = int(match.group(1)) if match else 0
        
        budget_places = int(values[3]) if len(values) > 3 and values[3].isdigit() else 0
        paid_places = int(values[4]) if len(values) > 4 and values[4].isdigit() else 0
        
        
    

        if budget_places > 0:
            item = {
                'id': id,
                'code': code,
                'title': title,
                'description': description,
                'base': base,
                'group_type': 'FREE',
                'duration_years': years+1,
                'places': budget_places,
                'minScore': find_minScore(code, base, groupType = "FREE")
            }
            table_data.append(item)

        if paid_places > 0:
            item = {
                'id': id,
                'code': code,
                'title': title,
                'description': description,
                'base': base,
                'group_type': 'COMMERCIAL',
                'duration_years': years+1,
                'places': paid_places,
                'cost': costs_data.get(code),
                'minScore': find_minScore(code, base, groupType="COMMERCIAL")
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
        title = code_name[9:]
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
        min_score = None

        if paid_places > 0:
            item = {
                'id': id,
                'code': code,
                'title': title,
                'description': description,
                'base': base,
                'group_type': "EXTRAMURAL",
                'duration_years': years+1,
                'places': paid_places,
                'cost': extramural_costs_data.get(code),
                'minScore': min_score
            }
            extramural_table_data.append(item)

    return extramural_table_data


def parse_rating(): #

    logger.debug("Starting parse rating table")
    rating_url = 'http://nke.ru/applicants/the_admissions_committee/reyting-abiturientov.php'

    try:
        rating_response = requests.get(rating_url)
        if rating_response.status_code != 200:
            logger.warning(f"Page of rating is not available: {rating_response.status_code}")

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
            statementQuantity = int(values[2]) if len(values) > 2 and values[2].isdigit() else 0
            competition = float(values[3]) if len(values) > 3 else 0.0

            item = {
                'code': code,
                'name': name,
                'plan': plan,
                'statementQuantity': statementQuantity,
                'competition': competition,
                'base': current_base,
                'skill': current_qualification
            }
            rating_table_data.append(item)

        logger.debug("Successfully parsed rating table")
        return rating_table_data
    

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while parsing Rating table: {e}", exc_info=True)
        return None
    
    except Exception as e:
        logging.critical(f"Critical Rating table parsing error: {e}", exc_info=True)
        return None


def parse_educational_loan(): #

    logger.debug("Starting Educational loan parsing")
    loan_url = 'http://www.nke.ru/applicants/educational-loan/the-project/'

    try:
        loan_response = requests.get(loan_url)
        if loan_response.status_code != 200:
            logger.warning(f"Page Educational loan is not available: {loan_response.status_code}")
            return None

        loan_soup = BeautifulSoup(loan_response.text, 'html.parser')


        loan_content = loan_soup.find('div', class_='white-box col-margin-bottom padding-box')
        if not loan_content:
            logger.warning(f"Educational loan block was not found")
            return None
        
        loan_content_data = []
        if loan_content:
            for h in loan_content.find_all('h1'):
                title = h.get_text(strip=True)
                if title:
                    loan_content_data.append(f'# {title}')
            for p in loan_content.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    if "хотите узнать больше?" in text.lower() or "переходите в раздел" in text.lower():
                        continue
                    else:
                        loan_content_data.append(text)
        loan_content_md = educational_loan_md(loan_content_data)

        logger.debug("Successfully parsed Educational loan")
        return loan_content_md
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while parsing educational loan: {e}", exc_info=True)
        return None
    
    except Exception as e:
        logging.critical(f"Critical educational loan parsing error: {e}", exc_info=True)
        return None
    

def educational_loan_md(paragraphs):

    markdown_lines = []
    i = 0
    while i<len(paragraphs):
        line = paragraphs[i]
        if len(line)<100 and (line.endswith('?') or line.endswith(':')):
            markdown_lines.append(f'### {line}')
            i+=1
        elif line.startswith('•'):
            markdown_lines.append('')
            while i < len(paragraphs) and (paragraphs[i].startswith('•')):
                item = paragraphs[i].lstrip('•').strip()
                markdown_lines.append(f' - {item}')
                i+=1
            markdown_lines.append('')
        else:
            markdown_lines.append(line)
            i+=1

    return '\n'.join(markdown_lines)


def parse_all_data():#
    
    logger.debug("Starting all_data parsing")
    
    url = 'http://www.nke.ru/applicants/directions_specialty_exams/'
    
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            logger.warning(f"Page of specialties not found: {response.status_code}")
            raise Exception(f"Page not found: {response.status_code}")

        

        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        

        if len(tables) < 3:
            logger.warning("Less than 3 tables")
            raise Exception("Less than 3 tables")

        intramural_not_full_table = tables[0]
        intramural_full_table = tables[1]
        extramural_table = tables[2]

       
        logger.debug("Parsing NOT_FULL table")
        try:
            data1 = parse_table_intramural(intramural_not_full_table, base="NOT_FULL", costs_data=parse_cost_of_training_intramural())
        except Exception as e:
            logger.error(f"Error while parsing NOT_FULL table: {e}", exc_info=True)
            raise Exception('Error while parsing NOT_FULL table')

        logger.debug("Parsing FULL table")
        try:
            data2 = parse_table_intramural(intramural_full_table, base="FULL", costs_data=parse_cost_of_training_extramural())
        except Exception as e:
            logger.error(f"Error while parsing FULL table: {e}", exc_info=True)
            raise Exception('Error while parsing FULL table')

        logger.debug("Parsing EXTRAMURAL table")
        try:
            data3 = parse_extramural_table(extramural_table, extramural_costs_data=parse_cost_of_training_extramural())
        except Exception as e:
            logger.error(f"Error while parsing EXTRAMURAL table: {e}", exc_info=True)
            raise Exception('Error while parsing EXTRAMURAL table')

       
        main_data = data1 + data2 + data3

        if not main_data:
            logger.warning("All 3 tables is None")
            return []

        logger.debug(f"Successfully parsed all_data table")
        return main_data

    except Exception as e:
        logger.critical(f"Critical all_data parsing error: {e}", exc_info=True)
        return []
    