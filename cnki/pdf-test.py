"""
Created on 2019/3/11 16:33

@author: zhouweixin
@note: 
"""
import os
from pdfminer.pdfparser import PDFParser, PDFDocument


path = r'D:\助研\成程老师\20190220\pdf'
files = os.listdir(path)
files = [file for file in files if file.endswith('.pdf')]
for file in files:
    print(file)
    with open(os.path.join(path, file), 'rb') as f:
        # 创建解析器
        parser = PDFParser(f)
        # 创建文档
        doc = PDFDocument()
        # 链接解析器和文档
        parser.set_document(doc)
        doc.set_parser(parser)

        doc.initialize()

        if doc.is_extractable:
            print('支持txt转换')
        else:
            print('不失支持')
