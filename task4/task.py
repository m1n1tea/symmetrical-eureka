import json
import numpy as np




def find_min_x(points, z):
    """
    Находит минимальный x, при котором f(x) >= z для кусочно-линейной функции.
    
    Args:
        points: Список кортежей [(x1, y1), (x2, y2), ...], отсортированный по x
        z: Пороговое значение
    
    Returns:
        Минимальный x, при котором f(x) >= z, или argmax_x(f(x)), если такого x нет
        в формате (x, min(f(x),z))
    """
    if not points:
        return None
    
    # Проверяем первую точку
    if points[0][1] >= z:
        return points[0][0]
    
    # Проходим по всем отрезкам
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        
        # Если в начале отрезка условие уже выполняется
        if y1 >= z:
            return x1, z
        if x2 == x1 or y1 == y2:
            continue  # избегаем деления на ноль
        
        # Находим точку пересечения с уровнем z
        # Уравнение прямой: y = y1 + k*(x - x1), где k = (y2 - y1)/(x2 - x1)
        # Решаем y1 + k*(x - x1) = z
        
        # Проверяем, лежит ли z между y1 и y2
        if (y1 < z <= y2) or (y1 > z >= y2):
            # Вычисляем коэффициент наклона
            k = (y2 - y1) / (x2 - x1)
            # Находим x, где функция пересекает z
            x_intersect = x1 + (z - y1) / k
            return x_intersect, z
    
    # возвращаем argmax_x(f(x))
    max_y = max(y for x, y in points)

    for x, y in points:
        if y == max_y:
            return x, y

    # Не должно сюда дойти
    return None

    
def _membership_function(x, points):
    """
    Вычисляет значение функции принадлежности в точке x
    на основе заданных точек кусочно-линейной функции
    
    points: список пар [x, y], отсортированный по x
    """
    # Если x за пределами крайних точек
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    
    # Ищем интервал, в который попадает x
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        
        if x1 <= x <= x2:
            # Линейная интерполяция
            if x1 == x2:
                return max(y1, y2)
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    
    return 0.0

def _fuzzify_temperature(temp, temp_terms):
    """
    Фаззификация температуры
    
    Возвращает словарь {терм: степень_принадлежности}
    """
    result = {}
    for term in temp_terms:
        term_id = term["id"]
        points = term["points"]
        result[term_id] = _membership_function(temp, points)
    return result

def _apply_rules(fuzzy_temp, rules, heat_terms):
    """
    Применение правил логического вывода по методу Мамдани
    
    Возвращает активированные нечеткие множества для управления
    """
    activated_sets = []
    
    for rule in rules:
        temp_term, heat_term = rule
        
        # Уровень активации правила
        activation_level = fuzzy_temp.get(temp_term, 0.0)
        
        if activation_level > 0:
            # Находим функцию принадлежности для терма управления
            heat_mf = None
            for term in heat_terms:
                if term["id"] == heat_term:
                    heat_mf = term
                    break
            
            if heat_mf:
                # Создаем усеченную функцию принадлежности (min-активация)
                activated_set = {
                    "term": heat_term,
                    "activation": activation_level,
                    "points": heat_mf["points"]
                }
                activated_sets.append(activated_set)
    
    return activated_sets

def main(temp_mf_json, heat_mf_json, rules_json, current_temp):
    """
    Основная функция для расчета оптимального управления
    
    Параметры:
    - temp_mf_json: JSON-строка с функциями принадлежности для температуры
    - heat_mf_json: JSON-строка с функциями принадлежности для уровня нагрева
    - rules_json: JSON-строка с правилами логического вывода
    - current_temp: текущая температура (вещественное число)
    
    Возвращает: оптимальное значение управления (вещественное число)
    """
    try:
        # Парсинг JSON
        temp_data = json.loads(temp_mf_json)
        heat_data = json.loads(heat_mf_json)
        rules = json.loads(rules_json)
        
        # Извлекаем данные
        temp_terms = temp_data.get("температура", [])
        heat_terms = heat_data.get("температура", [])
        
        #Фаззификация температуры
        fuzzy_temp = _fuzzify_temperature(current_temp, temp_terms)
        
        #Применение правил логического вывода
        activated_sets = _apply_rules(fuzzy_temp, rules, heat_terms)
        
        if not activated_sets:
            return 0.0  # Нет активированных правил
        
        # Определим кандидатов для дефаззификации
        candidates = [find_min_x(set_["points"], set_["activation"]) for set_ in activated_sets]

        # Выбираем оптимальное управление по первому максимуму
        optimal_control =None

        max_val = max(y for x, y in candidates)
        for x, y in candidates:
            if y == max_val:
                optimal_control = x
        
        return float(optimal_control)
        
    except Exception as e:
        print(f"Ошибка при расчете управления: {e}")
        return 0.0





