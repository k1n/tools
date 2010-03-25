#!/usr/bin/python
# coding: utf-8

import os
import sys

chinese_dict = {
    '文件': '档案',
    '工具栏': '工具列',
    '快捷键': '捷径键',
    '软件': '软体',
    '应用程序': '应用程式',
    '界面': '介面',
    '标签': '分页',
    '支持': '支援',
    '搜索': '搜寻',
    '文件夹': '资料夹',
    '导入': '汇入',
    '导出': '汇出',
    '智能': '智慧',
    '扩展': '附加元件',
    '插件': '外挂程式',
    '链接': '連結',
    '归档': '备存',
    '收件夹': '收件匣',
    '终端': '终端机',
    '窗口': '視窗',
    '高级': '进阶',
    '“': '「',
    '”': '」',
}

if len(sys.argv) != 2:
    print 'Please follow by a file name'
    sys.exit(1)
else:
    orignal_data = open(sys.argv[1]).read()

    for k, v in chinese_dict.items():
        orignal_data = orignal_data.replace(k, v)

    new_path = sys.argv[1] + '.new'
    new_file = open(new_path, 'w')
    new_file.write(orignal_data)
    new_file.close()
