import os
import re
import pandas as pd
import shutil
import sys
import mysql.connector as mysql


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
                content = f.read().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').replace('..',
                                                                                                                  '')
                content = content[:min(len(content), 1000)]
            for keyword in keywords:
                if keyword in content:
                    print(file)
                    shutil.copy(os.path.join(in_path, file), os.path.join(keyword, file))

    print('筛选完成')


def rev(in_path='txt',
        keywords=[],
        title_content=0,
        fun=5):
    if not fun == 5:
        return

    print("【删除函数】")

    if not os.path.exists(in_path):
        print('路径不存在：' + in_path)

    files = os.listdir(in_path)
    if title_content == 0:
        for file in files:
            for keyword in keywords:
                if keyword in file:
                    print(file)
                    os.remove(os.path.join(in_path, file))
                    break
    else:
        for file in files:
            with open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore') as f:
                content = f.read().replace(' ', '').replace('\t', '').replace('\n', '') \
                    .replace('\r', '').replace('..', '')

            for keyword in keywords:
                if keyword in content:
                    print(file)
                    os.remove(os.path.join(in_path, file))
                    break

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


def merge(in_path='source',
          out_path='target',
          fun=8):
    if not fun == 8:
        return

    print("【归整文件】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    os.mkdir(out_path) if not os.path.exists(out_path) else 1

    dirs = os.listdir(in_path)
    for dir in dirs:
        files = os.listdir(os.path.join(in_path, dir))
        for file in files:
            print("copy: " + file)
            shutil.copy(os.path.join(in_path, dir, file), os.path.join(out_path, file))

    print('归整完成')


def extract_from_baodao(in_path='baodao',
                        database='baodao',
                        table='dada',
                        user='root',
                        password='root',
                        fun=9):
    if not fun == 9:
        return

    print("【报道信息提取】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    # 失败的文件名
    failed_file = 'match_failed_files.txt'  # 匹配失败错误的文件名
    conflict_file = 'match_conflict_files.txt'  # 匹配冲突错误的文件名(匹配到多个)
    dup_file = 'match_dup_files.txt'  # 重复错误的文件名

    # 删除失败的文件
    # os.remove(failed_file) if os.path.exists(failed_file) else 1
    # os.remove(conflict_file) if os.path.exists(conflict_file) else 1
    # os.remove(dup_file) if os.path.exists(dup_file) else 1

    # 连接数据库：user用户名，password密码，database数据库名
    conn = mysql.Connect(user=user, password=password, database=database)
    cursor = conn.cursor()

    # 所有待导入的文件
    files = os.listdir(in_path)
    for i, file in enumerate(files):
        sys.stdout.write('\r%d / %d' % (i + 1, len(files)))

        # 从文件名里提取标题
        title = file

        # 去除000.txt
        if len(title) > 7:
            title = title[:-7]

        # 去除中英文的空格，把_替换成:
        title = title.replace("_", ':').replace(" ", '').replace("　", '')

        # 读入文件
        with open(os.path.join(in_path, file), 'r', encoding='gbk', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            # 提取报杜名称和日期
            if '报' in line and '年' in line and '月' in line and '日' in line:
                line = line.replace(' ', '').replace('/', '').replace('\n', '').replace('\r', '')
                match = re.search(r'(.*报)(\d{4})年(\d{1,2})月(\d{1,2})日', line)

                # 提取文件内容
                content = ''.join(lines).replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').replace(
                    '..', '')

                if match:
                    office = match.group(1)  # 报杜
                    year = match.group(2)  # 年
                    month = match.group(3)  # 月
                    day = match.group(4)  # 日

                    # 年月日拼接成日期
                    date = '%d-%02d-%02d' % (int(year), int(month), int(day))

                    update_sql = "update " + table + " set 内容=%s where 报纸名称=%s and 日期=%s and (LOCATE(%s, 题名) or LOCATE(题名, %s))"
                    query_sql = "select count(*) from " + table + " where 报纸名称=%s and 日期=%s and (LOCATE(%s, 题名) or LOCATE(题名, %s))"
                    query_sql1 = "select count(*) from " + table + " where 报纸名称=%s and 日期=%s and (LOCATE(%s, 题名) or LOCATE(题名, %s)) and LENGTH(内容)>0"

                    # 判断是否已经存在
                    cursor.execute(query_sql1, [office, date, title, title])
                    num = cursor.fetchone()[0]
                    if num > 0:
                        append(file, dup_file)

                    # 查询匹配到的个数
                    cursor.execute(query_sql, [office, date, title, title])
                    num = cursor.fetchone()[0]

                    if num == 0:  # 匹配失败
                        append(file, failed_file)
                    elif num == 1:  # 匹配成功
                        cursor.execute(update_sql, [content, office, date, title, title])
                        conn.commit()
                    else:  # 匹配冲突
                        append(file, conflict_file)

                break

    cursor.close()
    conn.close()

    print('处理完成')

    # 显示是否有匹配失败的文件
    num = getNum(failed_file)
    if num > 0:
        print('匹配失败的个数: %d, 请看文件: %s' % (num, failed_file))

    # 显示是否有匹配冲突的文件
    num = getNum(conflict_file)
    if num > 0:
        print('匹配多个的个数: %d, 请看文件: %s' % (num, conflict_file))

    # 显示是否有匹配重复的文件
    num = getNum(dup_file)
    if num > 0:
        print('匹配重复的个数: %d, 请看文件: %s' % (num, dup_file))


def append(msg, file):
    """
    添加内容
    :param msg:
    :param file:
    :return:
    """
    with open(file, 'a+', encoding='gbk', errors='ignore') as f:
        f.write(msg + '\n')


def getNum(file):
    """
    查询数量
    :param file:
    :return:
    """
    if not os.path.exists(file):
        return 0

    with open(file, 'r', encoding='gbk', errors='ignore') as f:
        return len(f.readlines())


def recover_filename(in_file='fileinfo.xlsx',
                     in_path='target',
                     fun=10):
    if not fun == 10:
        return

    print("【复原文件名】")

    if not os.path.exists(in_path):
        print('文件夹不存在：' + in_path)
        return

    if not os.path.exists(in_file):
        print('文件不存在：' + in_file)
        return

    headers = ['序号', '证券代码', '日期', '公告序号', '公司简称', '标题']
    datas = pd.read_excel(in_file, dtype=str)
    datas = datas.to_dict(orient='index')
    id2filename = {}
    for data in datas.values():
        id = data['序号']
        code = data['证券代码']
        date = data['日期']
        firm = data['公司简称']
        title = data['标题']

        filename = '%s-%s：%s(%s).txt' % (code, firm, title, date)
        id2filename[id] = filename

    files = os.listdir(in_path)
    for file in files:
        id = file.replace('.txt', '')
        if id in id2filename.keys():
            shutil.copy(os.path.join(in_path, file), os.path.join(in_path, id2filename[id]))

    print('复原完成')


def extract_info_import_db(in_path='txt',
                           database='yidaiyilu',
                           table='data',
                           user='root',
                           password='root',
                           fun=11):
    """
    根据文件名提取信息(编号)：【序号】，【证券代码】，【日期】，【公司简称】，【标题】，【公告序号】，【移动】
    :param in_path: 输入路径
    :param out_path: 输出路径
    :param out_file: 输出文件名
    :return:
    """
    if not fun == 11:
        return

    print("【提取信息到数据库】")

    if not os.path.exists(in_path):
        print("路径不存在：" + in_path)
        return;

    # 1.创建数据库
    conn = mysql.Connect(user=user, password=password)
    cursor = conn.cursor()
    cursor.execute("create database if not exists " + database)
    conn.commit()

    conn.database = database

    # 2.创建表
    sql = """CREATE TABLE IF NOT EXISTS `%s`  (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `文件名` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
              `证券代码` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
              `日期` date DEFAULT NULL,
              `公告序号` int(11) DEFAULT NULL,
              `公司简称` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
              `标题` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
              `内容` longtext CHARACTER SET utf8 COLLATE utf8_general_ci,
              PRIMARY KEY (`id`) USING BTREE
            ) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;""" % table
    cursor.execute(sql)
    conn.commit()

    sql = "INSERT INTO `" + table + "` (id, `文件名`, `证券代码`, `日期`, `公告序号`, `公司简称`, `标题`, `内容`) VALUES (null, %s, %s, %s, %s, %s, %s, %s);"
    codedate2num = {}

    files = os.listdir(in_path)
    err_files = []
    # 序号
    row_num = 0
    datas = []
    for i, file in enumerate(files):
        sys.stdout.write('\r%d / %d' % (i+1, len(files)))

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

            content = ''
            with open(os.path.join(in_path, file), encoding='gbk', errors='ignore') as f:
                content = f.read().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '').replace(
                    '..', '')

            # 添加到数据库
            cursor.execute(sql, [file, code, date, num, firm, title, content])
            conn.commit()

            datas.append(
                {'序号': row_num, '证券代码': str(code), '公司简称': firm, '标题': title, '日期': date, '公告序号': num, '移动': 0})
    print('\n提取完成')