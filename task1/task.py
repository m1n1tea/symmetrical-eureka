import re


def main(s: str, e: str) -> tuple[
    list[list[bool]],
    list[list[bool]],
    list[list[bool]],
    list[list[bool]],
    list[list[bool]]
]:
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

    # Инициализируем матрицы
    r1 = [[False] * n for _ in range(n)]  # непосредственное управление
    r2 = [[False] * n for _ in range(n)]  # непосредственное подчинение
    r3 = [[False] * n for _ in range(n)]  # опосредованное управление
    r4 = [[False] * n for _ in range(n)]  # опосредованное подчинение
    r5 = [[False] * n for _ in range(n)]  # соподчинение на одном уровне

    # Строим списки смежности для графа и обратного графа
    graph = [[] for v in vertices]

    tree = [-1 for v in vertices]

    for a, b in edges:
        i, j = vertex_to_idx[a], vertex_to_idx[b]
        graph[i].append(j)
        graph[j].append(i)

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
    dfs(vertex_to_idx[e], -1)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                r5[i][j] = r5[i][j] or (r1[k][i] and r1[k][j]) # соподчинение на одном уровне

    return r1, r2, r3, r4, r5
