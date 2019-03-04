"""
Created on 2019/3/3 16:26

@author: zhouweixin
@note:

公告已经被分成了n类，分别放在了n个文件夹，每个文件夹里有n_i个公告，公告是txt格式的
需要制作一个excel表，表格的第一列是公告日期，第二列是证券代码，第三列是公告标题，第四列及之后的列都是分类。
假如Excel中第四列是“购买股权”类，公告1属于“购买股权”类，已经被放置在“购买股权”文件夹中，则该公告在第四列取值为1，如果公告2不属于购买股权类，则第四列取值为0
同理，加入第五列是“担保”类，那么所有被放置在“担保”文件夹的公告在第五列的取值都为1，不属于这一类的公告取值为0。
如果一个公告既属于“购买股权”，又属于“担保”，则该公告在第四列和第五列的取值都为1。
"""
import os
import re
import pandas as pd


def start(in_path=r'分类', out_file='结果.xlsx'):
    """
    :param in_path: 输入文件夹
    :param out_file: 输出文件
    :return:
    """
    if not os.path.exists(in_path):
        print('不存在：' + in_path)
        return

    headers = ['公告日期', '证券代码', '公告标题']
    file2type = {}
    file2info = {}

    dirs = os.listdir(in_path)
    for dir in dirs:
        headers.append(dir)
        files = os.listdir(os.path.join(in_path, dir))
        for file in files:
            file2type.setdefault(file, []).append(dir)
            match = re.search('(\d{6})-(.*)\((\d{4}-\d{1,2}-\d{1,2})\).txt', file)
            if match:
                code = match.group(1)
                title = match.group(2)
                date = match.group(3)
                info = file2info.setdefault(file, {'公告日期': code, '证券代码': title, '公告标题': date})

                for d in dirs:
                    if d not in info:
                        info[d] = 0
                info[dir] = 1

    datas = pd.DataFrame(list(file2info.values()), columns=headers)
    datas.to_excel(out_file, header=headers, index=False)
    print('完成, 保存：' + out_file)

start()

