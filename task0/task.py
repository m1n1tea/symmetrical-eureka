# task0
#
# Условие:
# Дан ориентированный ациклический граф G = (V, E), где:
#   V -- множество вершин графа,
#   E -- множество рёбер графа.
#
# Каждое ребро ei принадлежит E и описывается парой (vj, vk), где:
#   vj, vk принадлежит V -- вершины графа.
#
# Граф задаётся в виде CSV-файла. Каждая строка файла соответствует одному ребру:
#   начальная вершина, конечная вершина
#
# Пример входных данных (graph.csv):
# 1,2
# 1,3
# 3,4
# 3,5
#
# Задача:
# 1. Написать функцию
#       def main(csv_graph: str) -> list[list[int]]]:
#          ...
#    где csv_graph -- строка (содержимое CSV-файла).
#
# 2. Функция должна возвращать матрицу смежности графа в виде списка списков list[list].
#    - Размер матрицы: n x n, где n = |V| (количество вершин графа).
#    - Элемент matrix[i][j] равен 1, если существует ребро из вершины i в вершину j, и 0, если ребра нет.
#
# Ожидаемый результат:
#  [[0, 1, 1, 0, 0],
#   [1, 0, 0, 0, 0],
#   [1, 0, 0, 1, 1],
#   [0, 0, 1, 0, 0],
#   [0, 0, 1, 0, 0]]


import re

def main(csv_graph: str) -> list[list[int]]:
    edges_text = csv_graph.splitlines()
    edges : list[list[int]] = []
    max_vertex_num = 0

    for edge in edges_text:
        a,b = re.split(';|,|, |; | ', edge,2)
        a = int(a)
        b = int(b)
        edges.append([a,b])
        max_vertex_num = max(max_vertex_num,a,b)
    matrix =[[0 for i in range(max_vertex_num)] for i in range(max_vertex_num)]

    for a,b in edges:
        matrix[a-1][b-1] = 1
        matrix[b-1][a-1] = 1

    return matrix