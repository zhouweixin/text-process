import re
import sys


matchers = re.finditer('(哈喽|你好|Hi)', '张三, 早上好, 哈喽啊, 你好啊, Hi啊')
for matcher in matchers:
    print(matcher.group(1))

matchers = re.finditer('(哈喽|你好|Hi)', '张三, 早上好')
for matcher in matchers:
    print("==")
    print(matcher.group(1))

# System.setProperty("webdriver.chrome.driver"  py)