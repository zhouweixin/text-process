from utils import *

# fun 取8个值：1表示执行【统计函数】，2表示执行【提取函数】，3表示执行【移动函数】，4表示执行【筛选函数】，5表示执行【删除函数】，
#              6表示执行【移动函数-根据标题移动】，7表示执行【去重函数-保留时间最小】，8表示执行【归整文件】，
#               9 表示执行【提取报道信息】函数
fun = 10

############################################################################################################
#   1.【统计函数】                                                                                         #
#   功能：根据文件名统计信息(编号)：【序号】，【证券代码】，【日期】，【公司简称】，【标题】，【公告序号】 #
#   参数说明：                                                                                             #
#     1.in_path: 公告文本所在的路径                                                                        #
#     2.out_path: 公告文本编码后所在的路径                                                                 #
#     3.out_file: 公告信息文件                                                                             #
#     4.fun: 为1时执行此函数                                                                               #
############################################################################################################
extract_info_by_filename(in_path='txt',
                         out_path='target_txt',
                         out_file='fileinfo.xlsx',
                         fun=fun)

############################################################################################################
#   2.【提取函数】                                                                                         #
#   功能：根据规则提取信息                                                                                 #
#   参数说明：                                                                                             #
#     1.in_path: 公告文本编码后所在的路径(与【统计函数】的out_path保持一致)                                #
#     2.out_file: 公告信息文件(与【统计函数】的out_file保持一致)                                           #
#     3.rule_names: 规则名列表(保证长度比下一个参数rules的长度小1)                                         #
#     4.rules: 规则列表                                                                                    #
#     5.max_len: 提取信息的最大长度                                                                        #
#     6.fun: 为2时执行此函数                                                                               #
############################################################################################################
# 根据规则提取信息： 1、中间不能有句号；(完成)2、添加一个是否移动的字段；(完成)3、可以同时提取2及以上信息（前中后）(完成)；4、打开编码错误的文件
extract_info_by_rule1(in_path='target_txt',
                      out_file='fileinfo.xlsx',
                      rule_names=['1'],
                      rules=['对', '影响'],
                      max_len=20,
                      fun=fun)

############################################################################################################
#   3.【移动函数】                                                                                         #
#   功能：移动指定文件到指定文件夹                                                                         #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径 (与【统计函数】的out_path保持一致)                                             #
#     2.in_file: 公告信息文件(与【统计函数】的out_file保持一致)                                            #
#     3.out_path: 目标文件路径                                                                             #
#     4.fun: 为3时执行此函数                                                                               #
############################################################################################################
move_file(in_path='target_txt',
          in_file='fileinfo.xlsx',
          out_path='分类1',
          fun=fun)

############################################################################################################
#   4.【筛选函数】                                                                                         #
#   功能：根据文件名或内容筛选文件到指定文件夹                                                             #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径, 不限文件格式                                                                  #
#     2.keywords: 搜索的关键字                                                                             #
#     3.title_content: 0表示标题, 1表示内容                                                                #
#     4.fun: 为4时执行此函数                                                                               #
############################################################################################################
select(in_path='txt',
       keywords=['中华人民共和国', '国际海洋资源股份有限公司'],
       title_content=1,
       fun=fun)

############################################################################################################
#   5.【删除函数】                                                                                         #
#   功能：根据文件名或内容删除文件                                                                         #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径, 不限文件格式                                                                  #
#     2.keywords: 删除的关键字                                                                              #
#     3.title_content: 0表示标题, 1表示内容                                                                #
#     4..fun: 为5时执行此函数                                                                              #
############################################################################################################
rev(in_path='txt',
    keywords=['中信建投证券股份有限公司接受金正大生态工程集'],
    title_content=1,
    fun=fun)

############################################################################################################
#   6.【移动函数-根据标题移动】                                                                            #
#   功能：根据600个excel的标题移动对应的公告                                                               #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径                                                                                #
#     2.in_file: 标题文件                                                                                  #
#     3.out_path: 目标文件路径                                                                             #
#     4.fun: 为6时执行此函数                                                                               #
############################################################################################################
move_file_by_title(in_path='政企合作移动文件功能测试文件/新建文件夹',
                   in_file='政企合作移动文件功能测试文件/一带一路测试文件.xlsx',
                   out_path='政企合作移动文件功能测试文件/目标文件夹',
                   fun=fun)

############################################################################################################
#   7.【去重函数-保留时间最小】                                                                            #
#   功能：同一公司的同一标题(括号前)认为是同一公告，保留时间最小                                           #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径                                                                                #
#     2.fun: 为7时执行此函数                                                                               #
############################################################################################################
clear(in_path='txt',
      fun=fun)

############################################################################################################
#   8.【归整文件】                                                                                         #
#   功能：归整文件到同一文件夹下                                                                           #
#   参数说明：                                                                                             #
#     1.in_path: 源文件路径(所有分类放入同一个文件夹下)                                                    #
#     2.out_path: 目标路径                                                                                 #
#     3.fun: 为8时执行此函数                                                                               #
############################################################################################################
merge(in_path='source',
      out_path='target',
      fun=fun)

############################################################################################################
#   9.【提取报道信息】                                                                                     #
#   功能：提取标题，报社，日期，作者                                                                       #
#   参数说明：                                                                                             #
#     1.in_path: 报道文件路径(txt格式)                                                                     #
#     2.database: 数据库名                                                                                 #
#     3.table: 表名                                                                                        #
#     4.user: 用户名                                                                                       #
#     5.password: 密码                                                                                     #
#     6.fun: 为9时执行此函数                                                                               #
############################################################################################################
extract_from_baodao(in_path=r'D:\助研\成程老师\20190220\txt',
                    database='baodao',
                    table='data',
                    user='root',
                    password='root',
                    fun=fun)

############################################################################################################
#   10.【复原文件名】                                                                                      #
#   功能：复原文件名                                                                                       #
#   参数说明：                                                                                             #
#     1.in_file: fileinfo.xlsx                                                                             #
#     2.in_path: 输入文件夹                                                                                #
#     3.fun: 为10时执行此函数                                                                               #
############################################################################################################
recover_filename(in_file='fileinfo.xlsx',
                 in_path='target_txt',
                 fun=fun)
