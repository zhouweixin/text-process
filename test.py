import re

text = "小明','小刚\",\" 小李";
print(text)
text = re.sub(',', '', text)
print(text)


    