from task import main
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'graph.csv')

graph = open(filename, "r", encoding="utf-8").read()
matrix = main(graph)

print("Edges:")
print(graph)
print("Matrix:")
print(matrix)