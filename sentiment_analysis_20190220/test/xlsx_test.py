import pandas as pd
import os


datas = pd.DataFrame(data={'a':[1, 2, 3], 'b':[4, 5, 6]})
print(datas)

datas = pd.DataFrame(data=[{'a': 1, 'b': 4}, {'a': 2, 'b': 5}, {'a': 3, 'b': 6}])
print(datas)

results = []

for i, col2value in datas.to_dict(orient='index').items():
    print(col2value)
    if col2value['a'] == 1:
        col2value['c'] = '10'

    results.append(col2value)

datas = pd.DataFrame(data=results)
print(datas)