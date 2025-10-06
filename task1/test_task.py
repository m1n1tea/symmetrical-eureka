from task import main
import os

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'graph.csv')

graph = open(filename, "r", encoding="utf-8").read()
r1, r2, r3, r4, r5 = main(graph, "2")

print("Непосредственное управление:")
print(r1)
print("Непосредственное подчинение:")
print(r2)
print("Опосредованное управление:")
print(r3)
print("Опосредованное подчинение:")
print(r4)
print("Соподчинение на одном уровне:")
print(r5)