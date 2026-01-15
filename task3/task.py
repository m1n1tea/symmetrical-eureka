import json
from itertools import combinations
import numpy as np
from collections import defaultdict, deque



# Преобразуем ранжировки в возможные позиции списка
def rank_to_dict(rank):
    result = {}
    cnt = 1
    for item in rank:
        if isinstance(item, list):
            # Если элемент - список, все его элементы принадлежат одному классу
            for elem in item:
                result[elem] = set([cnt + i for i in range(len(item))])
            cnt += len(item)
        else:
            # Если элемент - число, он образует отдельный класс
            result[item] = set([cnt])
            cnt += 1
    return result

def get_contradiction_core(json_str1, json_str2):

    # Парсим JSON-строки
    rank1 = json.loads(json_str1)
    rank2 = json.loads(json_str2)
    
    dict1 = rank_to_dict(rank1)
    dict2 = rank_to_dict(rank2)
    
    # Cчиатем, что элементы ранжировок совпадают
    all_elements = dict1.keys()
    
    # Находим противоречия
    contradictions = []
    
    for elem1, elem2 in combinations(sorted(all_elements), 2):
        # избегаем перестановок
        if str(elem1) > str(elem2):
            continue
        

        rank11 = min(dict1[elem1])
        rank12 = min(dict1[elem2])

        rank21 = min(dict2[elem1])
        rank22 = min(dict2[elem2])

        #Если один судья не уверен, то возьмём мнение второго
        if rank11 == rank12 or rank21 == rank22:
            continue

        # мнения совпадают
        if (rank11 < rank12) == (rank21 < rank22):
            continue        


        contradictions.append((elem1, elem2))
    
    # Преобразуем результат в JSON-строку
    return contradictions



def parse_ranking(json_str):
    """Преобразует JSON-строку в список объектов/кластеров"""
    ranking = json.loads(json_str)
    return ranking

def get_all_objects(ranking):
    """Извлекает все уникальные объекты из ранжировки"""
    objects = set()
    for item in ranking:
        if isinstance(item, list):
            objects.update(str(x) for x in item)
        else:
            objects.add(str(item))
    return sorted(objects)

def build_relation_matrix(ranking, objects_map):
    """Строит матрицу отношений Y для ранжировки"""
    n = len(objects_map)
    Y = np.zeros((n, n), dtype=int)
    
    # Рефлексивность
    for i in range(n):
        Y[i, i] = 1
    
    # Преобразуем ранжировку в последовательность кластеров
    clusters = []
    for item in ranking:
        if isinstance(item, list):
            clusters.append([str(x) for x in item])
        else:
            clusters.append([str(item)])

    # Заполняем матрицу отношений
    for i, cluster_i in enumerate(clusters):
        # Отношения внутри кластера
        for obj_i in cluster_i:
            idx_i = objects_map[obj_i]
            for obj_j in cluster_i:
                idx_j = objects_map[obj_j]
                Y[idx_i, idx_j] = 1
        
        # Отношения между кластерами (i предшествует j)
        for j, cluster_j in enumerate(clusters):
            if i < j:
                for obj_i in cluster_i:
                    idx_i = objects_map[obj_i]
                    for obj_j in cluster_j:
                        idx_j = objects_map[obj_j]
                        Y[idx_i, idx_j] = 1
    
    return Y


def warshall_algorithm(E):
    """Алгоритм Уоршелла для транзитивного замыкания"""
    n = E.shape[0]
    E_star = E.copy()
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if E_star[i, k] == 1 and E_star[k, j] == 1:
                    E_star[i, j] = 1
    
    return E_star

def find_clusters(E_star, objects):
    """Находит кластеры как компоненты связности"""
    n = E_star.shape[0]
    visited = [False] * n
    clusters = []
    
    for i in range(n):
        if not visited[i]:
            cluster = []
            for j in range(n):
                if E_star[i, j] == 1 and E_star[j, i] == 1:
                    cluster.append(objects[j])
                    visited[j] = True
            clusters.append(sorted(cluster))
    
    return clusters

def main(json_str1, json_str2):
    """Основная функция построения согласованной ранжировки"""
    
    ranking_a = json.loads(json_str1)
    ranking_b = json.loads(json_str2)
    # 1. Подготовка данных
    objects_set = set()
    objects_set.update(get_all_objects(ranking_a))
    objects_set.update(get_all_objects(ranking_b))
    objects = sorted(objects_set)
    n = len(objects)
    
    objects_map = {obj: i for i, obj in enumerate(objects)}
    
    # Построение матриц отношений
    Y_A = build_relation_matrix(ranking_a, objects_map)
    Y_B = build_relation_matrix(ranking_b, objects_map)
    
    # 2. Выявление противоречий
    Y_A_T = Y_A.T
    Y_B_T = Y_B.T
    
    S = get_contradiction_core(json_str1, json_str2)
    # 3. Построение согласованного порядка
    C = Y_A * Y_B

    
    # Учет противоречий
    for (i, j) in S:
        C[i, j] = 1
        C[j, i] = 1
    
    # 4. Определение кластеров

    C_T = C.T
    E = C * C_T

    E_star = warshall_algorithm(E)

    # 5. Выделение кластеров
    clusters = find_clusters(E_star, objects)
    
    # 6. Упорядочивание кластеров
    # Создаем отображение объекта на его кластер
    obj_to_cluster = {}
    for cluster_idx, cluster in enumerate(clusters):
        for obj in cluster:
            obj_to_cluster[obj] = cluster_idx
    
    # Строим матрицу порядка между кластерами
    k = len(clusters)
    cluster_order = np.zeros((k, k), dtype=int)
    
    for i in range(k):
        for j in range(k):
            if i != j:
                # Проверяем все пары объектов из разных кластеров
                order_consistent = True
                for obj_i in clusters[i]:
                    for obj_j in clusters[j]:
                        idx_i = objects_map[obj_i]
                        idx_j = objects_map[obj_j]
                        if C[idx_i, idx_j] == 0:
                            order_consistent = False
                            break
                    if not order_consistent:
                        break
                
                if order_consistent:
                    cluster_order[i, j] = 1
    
    # Топологическая сортировка кластеров
    indegree = [0] * k
    for i in range(k):
        for j in range(k):
            if cluster_order[i, j] == 1:
                indegree[j] += 1
    
    queue = deque([i for i in range(k) if indegree[i] == 0])
    sorted_clusters = []
    
    while queue:
        current = queue.popleft()
        sorted_clusters.append([int(x) for x in clusters[current]])
        
        for j in range(k):
            if cluster_order[current, j] == 1:
                indegree[j] -= 1
                if indegree[j] == 0:
                    queue.append(j)
    
    # 7. Формирование результата
    result = []
    for cluster in sorted_clusters:
        if len(cluster) == 1:
            result.append(cluster[0])
        else:
            result.append(cluster)
    
    return json.dumps(result)