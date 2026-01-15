from task import get_contradiction_core, main
import json

json_str1 = '[1,[2,3],4,[5,6,7],8,9,10]'
json_str2 = '[[1,2],[3,4,5],6,7,9,[8,10]]'

result = get_contradiction_core(json_str1, json_str2)
print("Матрица противоречий:")
print(json.dumps(result))  # Вывод: [[8,9]]

result = main(json_str1, json_str2)
print("Согласованная кластерная ранжировка:")
print(result)