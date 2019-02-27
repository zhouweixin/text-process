import re
import os
import pandas as pd
import sys
import shutil


def code_file(in_path='txt',
              out_path='target',
              out_file='codefile.xlsx',
              fun=1):
    """
    功能：给文件从1开始编码，并转存
    :param in_path: 源文件夹
    :param out_path: 目标文件夹
    :param out_file: 目标文件
    :return:
    """

    if not fun == 1:
        return

    print("【统计函数】")

    if not os.path.exists(in_path):
        print("不存在：" + in_path)
        return

    os.mkdir(out_path) if not os.path.exists(out_path) else 1

    id2file = []

    print('开始')
    files = os.listdir(in_path)
    for i, file in enumerate(files):
        sys.stdout.write('\r%d / %d' % (i + 1, len(files)))
        open(os.path.join(out_path, str(i + 1) + '.txt'), 'w', encoding='gbk').write(
            open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore')
                .read().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', ''))

        id2file.append(file)

    codedata = pd.DataFrame(data={'ID': list(range(1, len(files) + 1)), '文件名': id2file}, columns=['ID', '文件名'])
    codedata.to_excel('' + out_file, index=False)
    print('\n统计完成')


def load_stopwords():
    """
    功能：加载停止词
    :return:
    """
    # load stopwords
    stopwords = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    return stopwords


def load_catigories(filename='4分类情感字典.xlsx'):
    """
    功能：加载分类字典
    :param filename:
    :return:
    """
    # 分类名称(分类字典表)
    categories = ["Positive", "Negative", "Definite", "Ambiguous"]

    # 加载分类字典
    category2words = {}
    data = pd.read_excel(filename, names=categories)
    for category in categories:
        category2words[category] = [word for word in list(data[category]) if not pd.isna(word)]

    return category2words


def classify(in_path='target',
             in_file='codefile.xlsx',
             out_file='分类结果.xlsx',
             duplicate=True,
             fun=2):
    if not fun == 2:
        return

    print("【分类函数】")

    # 1.获取分类字典
    category2words = load_catigories()
    wordre2category = {'(' + '|'.join(words) + ')': category for category, words in category2words.items()}

    file2category2matcherwords = {}

    # 2.获取文件内容, 并统计出现的词
    files = os.listdir(in_path)
    for i, file in enumerate(files):
        sys.stdout.write('\r%d / %d' % (i + 1, len(files)))
        file2category2matcherwords[file.replace('.txt', '')] = {}
        with open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()
            for wordre, category in wordre2category.items():
                matchers = re.finditer(wordre, content)
                matcher_words = []
                for matcher in matchers:
                    matcher_words.append(matcher.group(1))

                # 是否重复
                if not duplicate:
                    matcher_words = list(set(matcher_words))

                file2category2matcherwords[file.replace('.txt', '')][category] = matcher_words

    for category in category2words.keys():
        os.mkdir(category) if not os.path.exists(category) else 1

    results = []
    # 3.存储结果
    datas = pd.read_excel(in_file)
    for i, col2value in datas.to_dict(orient='index').items():
        sys.stdout.write('\r%d / %d' % (i + 1, len(files)))
        file = str(col2value['ID'])

        category2num = {}
        for category in category2words.keys():
            words = file2category2matcherwords[file][category]
            col2value[category] = ";".join(words)
            category2num[category] = len(words)

        # 考虑多个最大值
        max_num = max(category2num.values())
        categories = [category for category, num in category2num.items() if num == max_num]
        col2value['分类结果'] = ';'.join(categories)
        results.append(col2value)
        for category in categories:
            shutil.copy(os.path.join(in_path, file + ".txt"), os.path.join('', category, file + ".txt"))

    colnames = ['ID', '文件名', '分类结果']
    colnames.extend(category2words.keys())
    result = pd.DataFrame(results, columns=colnames)
    result.to_excel(out_file, columns=colnames, index=False)
    print('\n分类完成: ' + out_file)
