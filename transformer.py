from collections import defaultdict
from parser import parse_all_data

def convert_to_specialty_schema(data_list):
    grouped = defaultdict(list)

    # Шаг 2: Группируем записи по ключу (code, title, description)
    for item in data_list:
        # Ключ для группировки — уникальный набор полей
        key = (item['code'], item['title'], item['description'])
        # Добавляем текущий элемент в группу
        grouped[key].append(item)

    # Шаг 3: Подготавливаем финальный результат
    result = []

    # Шаг 4: Обрабатываем каждую группу (одну специальность)
    for (code, title, description), items in grouped.items():
        group_types = []         # список всех типов набора (FREE, COMMERCIAL...)
        full_years = None        # длительность на базе 11 кл.
        not_full_years = None    # длительность на базе 9 кл.

        # Шаг 5: Перебираем все записи внутри одной специальности
        for item in items:
            base = item["base"]
            group_type = item["group_type"]

            # Пытаемся привести min_score к числу, если возможно
            try:
                min_score = float(item["minScore"]) if item["minScore"] and item["minScore"].isdigit() else None
            except Exception:
                min_score = None

            # Формируем объект GroupTypeSpec
            group_spec = {
                "type": group_type,
                "base": base,
                "years": item["duration_years"],
                "places": item["places"],
                "cost": item.get("cost"),
                "minScore": min_score
            }

            # Добавляем его в общий список
            group_types.append(group_spec)

            # Сохраняем длительность обучения по базе
            if base == "FULL":
                full_years = item["duration_years"]
            elif base == "NOT_FULL":
                not_full_years = item["duration_years"]

        # Формируем итоговый объект SpecialtySchema
        specialty = {
            "title": title,
            "description": description,
            "prefix": None,             # первые 2 символа кода
            "code": code,
            # "fullYears": full_years,
            # "notFullYears": not_full_years,
            "groupTypes": group_types
        }

        # Добавляем в финальный список
        result.append(specialty)

    # Возвращаем готовый результат
    return result

