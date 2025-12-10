from task import get_contradiction_core, build_consistent_ranking
import json

json_str1 = '[1,[2,3],4,[5,6,7],8,9,10]'
json_str2 = '[[1,2],[3,4,5],6,7,9,[8,10]]'
# уменьшил на 1, так как str(10) < str(2), а так i < j => str(i) < str(j)

result = get_contradiction_core(json_str1, json_str2)
print("Матрица противоречий:")
print(json.dumps(result))  # Вывод: [[8,9]]

result = build_consistent_ranking(json_str1, json_str2)
print("Согласованная кластерная ранжировка:")
print(json.dumps(result))