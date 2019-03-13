"""
Created on 2019/3/11 16:16

@author: zhouweixin
@note: 
"""

import mysql.connector as mysql

conn = mysql.connect(user='root', password='root')
cursor = conn.cursor()
cursor.execute('create database if not exists demo');
