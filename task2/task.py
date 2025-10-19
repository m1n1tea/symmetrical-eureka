import re

from copy import deepcopy
import math


def compute_entropy(matrices) -> tuple[float, float]:
    n = len(matrices[0])
    k = len(matrices)
    
    total_entropy = 0.0
    
    for matrix in matrices:
        for i in range(n):
            p_i = 0
            for j in range(n):
                if i != j and matrix[i][j]:
                    p_i += 1
            p_i/=(n-1)
            if p_i > 0:
                total_entropy += p_i * math.log2(p_i)
    
    H = -total_entropy
    
    H_max = (1 / (math.e * math.log(2))) * n * k
    h = H / H_max if H_max > 0 else 0
    
    return H, h


def graph_to_components(graph) -> list[list]:
    n = len(graph)

    component = []
    result = []
    used = [False * n for _ in range(n)]

    def dfs(v):
        if used[v]:
            return
        used[v] = True
        component.append(v)
        for to in graph[v]:
            dfs(to)

    for i in range(n):
        if used[i]:
            continue
        dfs(i)
        result.append(deepcopy(component))
        component = []

    return result

def generate_graphs(edges : list, n):
    graph = [[] for _ in range(n)]
    graphs = []
    for i, j in edges:
        graph[i].append(j)
        graph[j].append(i)
    graphs.append(deepcopy(graph))

    print("Начальный граф")
    print(graph)

    for a,b in edges:
        graph[a].remove(b)
        graph[b].remove(a)
        components = graph_to_components(graph)
        if len(components) != 2:
            print("graph")
            print(graph)
            print("components")
            print(components)
        assert len(components) == 2, "tree should always split in two connected parts after removing edge"
        for i in components[0]:
            for j in components[1]:
                if (a,b) == (i,j) or (a,b) == (j,i):
                    continue
                graph[i].append(j)
                graph[j].append(i)
                graphs.append(deepcopy(graph))
                graph[i].remove(j)
                graph[j].remove(i)
        
        graph[a].append(b)
        graph[b].append(a)
    return graphs
                

def graph_to_mats(graph, root) -> tuple[
        list[list[bool]],
        list[list[bool]],
        list[list[bool]],
        list[list[bool]],
        list[list[bool]]
    ]:
        n = len(graph)
        # Инициализируем матрицы
        r1 = [[False] * n for _ in range(n)]  # непосредственное управление
        r2 = [[False] * n for _ in range(n)]  # непосредственное подчинение
        r3 = [[False] * n for _ in range(n)]  # опосредованное управление
        r4 = [[False] * n for _ in range(n)]  # опосредованное подчинение
        r5 = [[False] * n for _ in range(n)]  # соподчинение на одном уровне
        stack = []
        def dfs(v, p):
            for a in stack:
                if a == p:
                    r1[a][v] = True  # непосредственное управление
                    r2[v][a] = True  # непосредственное подчинение
                else:
                    r3[a][v] = True # опосредованное управление
                    r4[v][a] = True # опосредованное подчинение
            for to in graph[v]:
                if to == p:
                    continue
                stack.append(v)
                dfs(to, v)
                stack.pop()
        dfs(root, -1)

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for k in range(n):
                    r5[i][j] = r5[i][j] or (r1[k][i] and r1[k][j]) # соподчинение на одном уровне

        return r1, r2, r3, r4, r5


def main(s: str, e: str) -> tuple[ float, float]:
    # Парсим CSV строку и получаем список рёбер
    edges = []
    for line in s.strip().split('\n'):
        if line:
            a, b = re.split(';|,| ', line, 2)
            edges.append((a.strip(), b.strip()))

    # Собираем все вершины графа
    vertices = set()
    for a, b in edges:
        vertices.add(a)
        vertices.add(b)
    vertices = sorted(vertices)  # Сортируем для детерминированного порядка

    # Создаем mapping вершина -> индекс
    vertex_to_idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)

    edge_indexes = []

    for a, b in edges:
        edge_indexes.append((vertex_to_idx[a],vertex_to_idx[b]))
    graphs = generate_graphs(edge_indexes, n)

    best_H = -float('inf')
    best_h = 0
    best_graph = None
    for graph in graphs:
        matrices = graph_to_mats(graph, vertex_to_idx[e])
        H , h = compute_entropy(matrices)
        #print(f"Граф: {graph}")
        #print(f"Энтропия: {H}")

        if H > best_H:
            best_H = H
            best_h = h
            best_graph = graph

    if best_graph:
        print(f"\nЛучший вариант перестановки:")
        print(f"Лучший Граф: {best_graph}")
    return best_H,best_h
