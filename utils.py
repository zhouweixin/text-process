import os
import re
import pandas as pd
import shutil
import sys


def extract_info_by_filename(in_path='txt',
                             out_path='target_txt',
                             out_file='fileinfo.xlsx',
                             fun=1):
    """
    根据文件名提取信息(编号)：【序号】，【证券代码】，【日期】，【公司简称】，【标题】，【公告序号】，【移动】
    :param in_path: 输入路径
    :param out_path: 输出路径
    :param out_file: 输出文件名
    :return:
    """
    if not fun == 1:
        return

    print("【统计函数】")

    os.mkdir(out_path) if not os.path.exists(out_path) else 1
    codedate2num = {}

    files = os.listdir(in_path)
    err_files = []
    # 序号
    row_num = 0
    datas = []
    for file in files:
        match = re.match('(\d{6})-(.*)：(.*)\((\d{4}-\d{1,2}-\d{1,2})\)', file)
        if match:
            # 证券代码
            code = match.group(1)
            # 公司简称
            firm = match.group(2)
            # 标题
            title = match.group(3)
            # 日期
            date = match.group(4)

            key = code + date
            num = codedate2num.setdefault(key, 0) + 1
            codedate2num[key] = num
            row_num += 1
            datas.append(
                {'序号': row_num, '证券代码': str(code), '公司简称': firm, '标题': title, '日期': date, '公告序号': num, '移动': 0})

            # 复制文件
            try:
                open(os.path.join(out_path, str(row_num) + '.txt'), 'w', encoding='gbk').write(
                    open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore').read().replace(' ',
                                                                                                           '').replace(
                        '\t',
                        '').replace(
                        '\n', '').replace('\r', ''))
            except:
                err_files.append(file)

    # 保存错误文件
    if err_files:
        with open('err_files.txt', 'w') as f:
            f.write('\n'.join(err_files))
            # f.writelines(err_files)

    datas = pd.DataFrame(datas)
    datas.to_excel(out_file, encoding='gbk', index=False, columns=['序号', '证券代码', '日期', '公告序号', '公司简称', '标题', '移动'])
    print('统计完成, 保存为：' + out_file)
    if len(err_files) > 0:
        print('失败文件数：' + str(len(err_files)) + ", 请查看err_files.txt文件")


def extract_info_by_rule(in_path='target_txt', out_file='fileinfo.xlsx', rule_name='测试', rule_start='关于',
                         rule_end='股份有限公司', max_len=20):
    """
    根据规则提取信息
    :param in_path: 输入路径
    :param out_file: 输出文件
    :param rule_name: 规则名
    :param rule: 规则
    :return:
    """

    if not os.path.exists(out_file):
        print('文件不存在：' + out_file)
        return

    rule = '%s(.+?)%s' % (rule_start, rule_end)

    row_num2value = {}
    row_num2context = {}

    files = os.listdir(in_path)
    for file in files:
        with open(os.path.join(in_path, file), 'r', encoding='gbk') as f:
            content = f.read()
            infos = re.findall(rule, content)
            infos = [info for info in infos if len(info) <= max_len]
            infos = sorted(infos, key=lambda x: len(x))

            if len(infos) > 0:
                row_num = file.replace('.txt', '')
                text = '%s%s%s' % (rule_start, infos[0], rule_end)
                idx = content.find(text)
                start_idx = max(0, idx - 50)
                end_idx = min(len(content), idx + 50 + len(text))
                row_num2value[row_num] = ';'.join(infos)
                row_num2context[row_num] = content[start_idx:end_idx]

    values = []
    contexts = []
    datas = pd.read_excel(out_file, dtype=str)
    for data in datas.iterrows():
        data = data[1]
        row_num = data['序号']
        if row_num in row_num2value:
            values.append(row_num2value[row_num])
            contexts.append(row_num2context[row_num])
        else:
            values.append('')
            contexts.append('')

    datas[rule_name] = values
    datas['上下文'] = contexts
    datas.to_excel(out_file, encoding='gbk', index=False,
                   columns=['序号', '证券代码', '日期', '公告序号', '公司简称', '标题', rule_name, '上下文'])
    print('提取完成, 保存为：' + out_file)


def extract_info_by_rule1(in_path='target_txt',
                          out_file='fileinfo.xlsx',
                          rule_names=['1', '2', '3'],
                          rules=['5.本人不存在', '第', '条所列', '的情形'],
                          max_len=20,
                          fun=2):
    """
    根据规则提取信息
    :param in_path: 输入路径
    :param out_file: 输出文件
    :param rule_name: 规则名
    :param rule: 规则
    :return:
    """

    if not fun == 2:
        return

    print("【提取函数】")

    if not len(rule_names) + 1 == len(rules):
        print('参数rules的个数要比rule_names大1')
        return

    if not os.path.exists(out_file):
        print('文件不存在：' + out_file)
        return

    rule = ''
    for r in rules:
        rule += r + '(.+?)'
    if len(rule) > 0:
        rule = rule[:len(rule) - 5]

    row_num2name2value = {}
    files = os.listdir(in_path)
    for i, file in enumerate(files):
        sys.stdout.write('\r%d / %d' % (i + 1, len(files)))
        if not os.path.exists(os.path.join(in_path, file)):
            continue

        with open(os.path.join(in_path, file), 'r', encoding='gbk') as f:
            content = f.read()
            search = re.finditer(rule, content)

            find = False
            for s in search:
                find = True
                for i in range(len(rule_names)):
                    strs = s.group(i + 1)
                    if '。' in strs or len(strs) > max_len:
                        find = False
                        break

                if find:
                    name2value = {}
                    for i, name in enumerate(rule_names):
                        name2value[name] = s.group(i + 1)
                    context = s.group()
                    break

            if find:
                # 序号
                row_num = file.replace('.txt', '')
                row_num2name2value[row_num] = {}
                # 上下文
                row_num2name2value[row_num]['context'] = context
                # 字段
                row_num2name2value[row_num]['values'] = name2value

                search = re.search('.{0,50}' + context + '.{0,50}', content)
                if search:
                    row_num2name2value[row_num]['context'] = search.group(0)

    datas = pd.read_excel(out_file, dtype=str)

    columns = datas.columns.values.tolist()
    columns.extend(rule_names)
    columns.append('上下文')
    datas = datas.reindex(columns=columns)
    for i, row in datas.iterrows():
        col_num = datas.shape[1] - 1
        row_num = row['序号']
        name2value = row_num2name2value.setdefault(row_num, {})
        datas.iloc[i, col_num] = name2value.setdefault('context', ' ')
        values = name2value.setdefault('values', {})
        for j, name in enumerate(rule_names):
            datas.iloc[i, col_num - len(rule_names) + j] = values.setdefault(name, ' ')

    datas.to_excel(out_file, encoding='gbk', index=False, columns=columns)
    print('\n提取完成, 保存为：' + out_file)


def move_file(in_path='target_txt', in_file='fileinfo.xlsx', out_path='分类1', fun=3):
    if not fun == 3:
        return

    print("【移动函数】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    if not os.path.exists(in_file):
        print('文件不存在：' + in_file)
        return

    # 创建目标路径
    os.mkdir(out_path) if not os.path.exists(out_path) else 1

    datas = pd.read_excel(in_file, dtype=str)
    for i, row in datas.iterrows():
        file = row['序号'] + '.txt'
        move = row['移动']
        if not os.path.exists(os.path.join(in_path, file)):
            continue

        if move == '1':
            print('move: ' + file)
            shutil.move(os.path.join(in_path, file), os.path.join(out_path, file))

    print('移动完成')


def select(in_path='txt',
           keywords=[],
           title_content=0,
           fun=4):
    if not fun == 4:
        return

    print("【筛选函数】")

    if not os.path.exists(in_path):
        print('路径不存在：' + in_path)

    for keyword in keywords:
        os.mkdir(keyword) if not os.path.exists(keyword) else 1

    files = os.listdir(in_path)
    if title_content == 0:
        print('通过【标题】筛选：')
        for file in files:
            for keyword in keywords:
                if keyword in file:
                    print(file)
                    shutil.copy(os.path.join(in_path, file), os.path.join(keyword, file))
    elif title_content == 1:
        print('通过【内容】筛选：')
        for file in files:
            with open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore') as f:
                content = f.read().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').replace('..', '')
                content = content[:min(len(content), 1000)]
                for keyword in keywords:
                    if keyword in content:
                        print(file)
                        shutil.copy(os.path.join(in_path, file), os.path.join(keyword, file))

    print('筛选完成')


def rev(in_path='txt',
        keyword='',
        fun=5):
    if not fun == 5:
        return

    print("【删除函数】")

    if not os.path.exists(in_path):
        print('路径不存在：' + in_path)

    files = os.listdir(in_path)
    for file in files:
        if keyword in file:
            print(file)
            os.remove(os.path.join(in_path, file))

    print('删除完成')


def move_file_by_title(in_path='D:/助研/成程老师/20190218/政企合作移动文件功能测试文件/新建文件夹',
                       in_file='D:/助研/成程老师/20190218/政企合作移动文件功能测试文件/一带一路测试文件.xlsx',
                       out_path='D:/助研/成程老师/20190218/政企合作移动文件功能测试文件/目标文件夹',
                       fun=6):
    if not fun == 6:
        return

    print("【移动函数-根据标题移动】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    if not os.path.exists(in_file):
        print('文件不存在：' + in_file)
        return

    # 创建目标路径
    os.mkdir(out_path) if not os.path.exists(out_path) else 1

    datas = pd.read_excel(in_file, dtype=str)
    colname = '标题'
    if colname not in datas.keys():
        print('标题文件不包含字段：' + colname)
        return

    titles = []
    for i, row in datas.iterrows():
        title = row[colname]
        if title == 'nan':
            continue

        titles.append(title)

    files = os.listdir(in_path)
    for file in files:
        for title in titles:
            if title in file:
                print('move: ' + file)
                shutil.move(os.path.join(in_path, file), os.path.join(out_path, file))
                break

    print('移动完成')


def clear(in_path='txt',
          fun=7):
    if not fun == 7:
        return

    print("【去重函数-保留时间最小】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    fileinfos = []
    files = os.listdir(in_path)
    for file in files:
        match = re.match(r'(\d{6})-(.*?)\(.*(\d{4}-\d{2}-\d{2})\)\.(txt|pdf)', file)
        if match:
            code = match.group(1)
            title = match.group(2)
            date = match.group(3)

            # 去掉冒号前的部分
            title = title.split("：")[1]
            # 前9个字相同认为就相同
            if len(title) > 9:
                title = title[0:9]

            fileinfos.append({
                'file': file,
                'code': code,
                'title': title,
                'date': date})

    code2title2date2file = {}
    for fileinfo in fileinfos:
        file = fileinfo['file']
        code = fileinfo['code']
        title = fileinfo['title']
        date = fileinfo['date']

        if code in code2title2date2file:
            title2date2file = code2title2date2file[code]
            if title in title2date2file:
                date2file = title2date2file[title]
                if date in date2file:
                    date2file[date].append(file)
                elif len(date2file.keys()) > 0:
                    d = list(date2file.keys())[0]
                    if d > date:
                        title2date2file[title] = {date: [file]}
            else:
                code2title2date2file[code][title] = {date: [file]}
        else:
            code2title2date2file[code] = {title: {date: [file]}}

    savefiles = []
    for title2date2file in code2title2date2file.values():
        for date2file in title2date2file.values():
            for date, fs in date2file.items():
                if len(fs) > 1:
                    is_find = False
                    for file in fs:
                        if '摘' in file:
                            is_find = True
                            savefiles.append(file)
                    if not is_find:
                        savefiles.extend(fs)
                else:
                    savefiles.extend(fs)

    for file in files:
        if file not in savefiles:
            print('delete：' + file)
            os.remove(os.path.join(in_path, file))
    print('去重完成')
