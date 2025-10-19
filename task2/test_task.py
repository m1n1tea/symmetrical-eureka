from task import main
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'graph.csv')

graph = open(filename, "r", encoding="utf-8").read()
H,h = main(graph, "2")

print("Абсолютная энтропия:")
print(H)
print("Относительная энтропия:")
print(h)