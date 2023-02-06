# __author__ = "huanghonghong"
import os
# import configparser

# config = configparser.ConfigParser()
# config.read('config.ini')

sourceTablePath = r'F:\x5\conf\TabFile'
clientLuaTablePath =  r'F:\x5\client\bin\Assets\Lua\Settings'
serverLuaTablePath = r'F:\x5\server\bin\win\luacode\conf\data'

fieldNameList = []
fieldTypeList = []
tableList = []

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def is_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def sourceTableToList(path,filterPrefix,removePrefix):
    # path = config.get('projectRoot','sourceTablePath') + '/' + tableName
    # path = sourceTablePath + '/' + tableName
    file = open(path,encoding='utf-16')

    for line in file.readlines():
        if (line[0] == '/' and line[0] == '/') or line[0] == '\t' or line[0] == ' ':
            continue
        curLine = line.strip('\n').split('\t')
        if curLine[0] == 'int':
            fieldTypeList = curLine
            continue
        if curLine[0] == 'id':
            fieldNameList = curLine
            continue
        tableList.append(curLine)
    file.close()

    strList = []

    # 表内容为空的情况
    if len(tableList) == 1 and len(tableList[0]) == 1 and tableList[0][0] == '':
        strList.append('local _M = {}')
        strList.append('return _M')
        return strList

    # 文件头
    strList.append('local _M = {}')

    for i in range(len(tableList)):
        lineStr = '' + '_M[' + tableList[i][0] + ']={'
        it = iter(range(len(tableList[i])))
        for j in it:
            # 过滤s_前缀struct和list
            if fieldTypeList[j] == 'struct' and fieldNameList[j].startswith(filterPrefix):
                structLength = 0
                while fieldTypeList[j + 1 + structLength] != 'struct':
                    structLength += 1
                for k in range(structLength + 1):
                    next(it)
                continue
            if fieldTypeList[j] == 'list' and fieldNameList[j].startswith(filterPrefix):
                listLength = 0
                while fieldTypeList[j + 1 + listLength] != 'list':
                    listLength += 1
                for k in range(listLength + 1):
                    next(it)
                continue

            # 过滤不导出的字段
            if fieldNameList[j].startswith('no_') or fieldNameList[j].startswith(filterPrefix):
                continue

            # 判断字段类型
            if fieldTypeList[j] == 'struct' and fieldNameList[j] != '':
                structLength = 0
                isValueAllNull = True
                while fieldTypeList[j + 1 + structLength] != 'struct':
                    if tableList[i][j + 1 + structLength] != '':
                        isValueAllNull = False
                    elif tableList[i][j + 1 + structLength] == '' and (fieldTypeList[j + 1 + structLength] == 'int' or fieldTypeList[j + 1 + structLength] == 'float' or fieldTypeList[j + 1 + structLength] == 'string' or fieldTypeList[j + 1 + structLength] == 'list<int>' or fieldTypeList[j + 1 + structLength] == 'list<int|>' or fieldTypeList[j + 1 + structLength] == 'luaTable'):
                        isValueAllNull = False
                    structLength += 1
                if isValueAllNull:
                    for n in range(structLength):
                        next(it)
                    continue

                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '={'
                # 有的struct可能首尾的name都不为空
                if fieldTypeList[j] == fieldTypeList[j + structLength + 1]:
                    fieldNameList[j + structLength + 1] = ''
                for k in range(structLength):
                    # 跳过structLength次列循环
                    next(it)
                    if tableList[i][k + j + 1] == '' and (fieldTypeList[k + j + 1] == 'int' or fieldTypeList[k + j + 1] == 'float'):
                        tableList[i][k + j + 1] = '0'
                    elif tableList[i][k + j + 1] == '' and fieldTypeList[k + j + 1] == 'luaTable':
                        tableList[i][k + j + 1] = 'nil'
                    elif tableList[i][k + j + 1] == '' and fieldTypeList[k + j + 1] == 'list<int>':
                        tableList[i][k + j + 1] = '{' + tableList[i][k + j + 1] + '}'
                    elif fieldTypeList[k + j + 1] == 'list<int|>':
                        lineStr = lineStr + remove_prefix(fieldNameList[k + j + 1],removePrefix) + '={' + tableList[i][k + j + 1].replace('|',',') + '},'
                        continue
                    lineStr = lineStr + remove_prefix(fieldNameList[k + j + 1],removePrefix) + '=' + tableList[i][k + j + 1].strip('"') + ','
                lineStr = lineStr.strip(',')

                lineStr = lineStr + '},'

            elif fieldTypeList[j] == 'list' and fieldNameList[j] != '':
                listLength = 0
                isValueAllNull = True
                while fieldTypeList[j + 1 + listLength] != 'list':
                    if tableList[i][j + 1 + listLength] != '':
                        isValueAllNull = False
                    elif tableList[i][j + 1 + listLength] == '' and (fieldTypeList[j + 1 + listLength] == 'int' or fieldTypeList[j + 1 + listLength] == 'luaTable' or fieldTypeList[j + 1 + listLength] == 'string' or fieldTypeList[j + 1 + listLength] == 'float'):
                        isValueAllNull = False
                    listLength += 1

                if isValueAllNull:
                    for n in range(listLength + 1):
                        next(it)
                    continue

                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '={'

                _it = iter(range(listLength))
                for k in _it:
                    # 跳过listLength次列循环
                    next(it)
                    if tableList[i][k + j + 1] == '' and fieldTypeList[k + j + 1] == 'luaTable':
                        continue
                    elif tableList[i][k + j + 1] == '' and (fieldTypeList[k + j + 1] == 'int' or fieldTypeList[k + j + 1] == 'float'):
                        tableList[i][k + j + 1] = '0'

                    elif fieldTypeList[k + j + 1] == 'string':
                        tableList[i][k + j + 1] = tableList[i][k + j + 1].replace('""','"')
                        lineStr = lineStr + '"' + tableList[i][k + j + 1].strip('"') + '",'
                        continue

                    # list里面嵌套struct
                    elif tableList[i][k + j + 1] == '' and fieldTypeList[k + j + 1] == 'struct' and fieldNameList[k + j + 1] != '':
                        structLength = 0
                        isValueAllNull = True
                        while fieldTypeList[k + j + 2 + structLength] != 'struct':
                            if tableList[i][k + j + 2 + structLength] != '':
                                isValueAllNull = False
                            structLength += 1
                        if isValueAllNull:
                            for n in range(structLength + 1):
                                next(it)
                                next(_it)
                            continue

                        lineStr = lineStr + '{'

                        for m in range(structLength):
                            if fieldNameList[m + k + j + 2] == 'no_remark' or fieldNameList[m + k + j + 2].startswith(filterPrefix):
                                continue
                            elif tableList[i][m + k + j + 2] == '' and (fieldTypeList[m + k + j + 2] == 'int' or fieldTypeList[m + k + j + 2] == 'float'):
                                tableList[i][m + k + j + 2] = '0'
                            elif fieldTypeList[m + k + j + 2] == 'bool':
                                if tableList[i][m + k + j + 2] == '0' or tableList[i][m + k + j + 2] == '' or tableList[i][m + k + j + 2] == 'FALSE':
                                    tableList[i][m + k + j + 2] = 'false'
                                else:
                                    tableList[i][m + k + j + 2] = 'true'
                            elif fieldTypeList[m + k + j + 2] == 'string':
                                tableList[i][m + k + j + 2] = tableList[i][m + k + j + 2].replace('""','"')
                                lineStr = lineStr + remove_prefix(fieldNameList[m + k + j + 2], removePrefix) + '="' + tableList[i][m + k + j + 2] + '",'
                                continue
                            elif fieldTypeList[m + k + j + 2] == 'list<int|>':
                                lineStr = lineStr + remove_prefix(fieldNameList[m + k + j + 2], removePrefix) + '={' + tableList[i][m + k + j + 2].replace('|',',') + '},'
                                continue
                            elif tableList[i][m + k + j + 2] == '' and fieldTypeList[m + k + j + 2] == 'luaTable':
                                tableList[i][m + k + j + 2] = 'nil'
                            lineStr = lineStr + remove_prefix(fieldNameList[m + k + j + 2], removePrefix) + '=' + tableList[i][m + k + j + 2].strip('"') + ','
                        for n in range(structLength + 1):
                            next(it)
                            next(_it)
                        lineStr = lineStr.strip(',')

                        lineStr = lineStr + '},'
                        continue

                    lineStr = lineStr + tableList[i][k + j + 1].strip('"') + ','
                lineStr = lineStr.strip(',')

                lineStr = lineStr + '},'

            elif fieldNameList[j] == '':
                continue

            elif fieldTypeList[j] == 'list<int|>':
                tableList[i][j] = tableList[i][j].replace('|',',')
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + '{' + tableList[i][j] + '}' + ','

            elif fieldTypeList[j] == 'list<string|>':
                if tableList[i][j] != '':
                    tableList[i][j] = '"' + tableList[i][j].replace('|','","') + '"'
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + '{' + tableList[i][j] + '}' + ','

            elif fieldTypeList[j] == 'int' or fieldTypeList[j] == 'float':
                if tableList[i][j] == '':
                    tableList[i][j] = '0'
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + tableList[i][j].strip(' ') + ','

            elif fieldTypeList[j] == 'bool':
                if tableList[i][j] == '0' or tableList[i][j] == '' or tableList[i][j] == 'FALSE':
                    tableList[i][j] = 'false'
                else:
                    tableList[i][j] = 'true'
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + tableList[i][j] + ','

            elif fieldTypeList[j] == 'string':
                tableList[i][j] = tableList[i][j].replace('""','"')
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + '"' + tableList[i][j].strip('"') + '"' + ','

            elif fieldTypeList[j] == 'list<int>':
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + '{' + tableList[i][j].strip('"') + '}' + ','

            elif fieldTypeList[j] == 'list<string>':
                if tableList[i][j] != '':
                    tableList[i][j] = '"' + tableList[i][j].replace(',','","').strip('"') + '"'
                else:
                    tableList[i][j] = tableList[i][j].replace(',','","')
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + '{' + tableList[i][j] + '}' + ','

            elif fieldTypeList[j] == 'luaTable':
                if tableList[i][j] == '':
                    tableList[i][j] = 'nil'
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + tableList[i][j].strip('"') + ','

            else:
                lineStr = lineStr + remove_prefix(fieldNameList[j],removePrefix) + '=' + tableList[i][j] + ','

        lineStr = lineStr.strip(',') + '}'
        strList.append(lineStr)

    # 文件尾
    strList.append('return _M')
    return strList

def clientLuaTableToList(tableName):
    # path = config.get('projectRoot','clientLuaTablePath') + '/' + tableName.replace('.txt','.lua')
    path = clientLuaTablePath + '/' + tableName.replace('.txt','.lua')
    file = open(path,encoding='utf-8')
    list = []
    for line in file.readlines():
        list.append(line.strip('\n'))
    file.close()
    return list

def serverLuaTableToList(tableName):
    # path = config.get('projectRoot','serverLuaTablePath') + '/' + tableName.replace('.txt', '.lua')
    path = serverLuaTablePath + '/' + tableName.replace('.txt','.lua')
    file = open(path,encoding='utf-8')
    list = []
    for line in file.readlines():
        list.append(line.strip('\n'))
    file.close()
    return list

def compareList(filename,list1,list2,endName):
    # print(list1)
    # print(list2)
    for i in range(len(list2)):
        if (list2[i].replace('\\\\','\\') == list1[i]) or (list2[i].replace('\\','') == list1[i]):
            # print(str(i + 1) + ':这行一样')
            continue
        else:
            print(endName + 'warning---------文件名: ' + filename + ' 可能没导表,可能填写不规范,也可能工具有漏铜！！！')
            # print(filename + ':第' + str(i + 1) + '行:这行不一样!!!!!!!!!!!!!')
            break

if __name__ == '__main__':
    # compareList(sourceTableToClientList('skill'),clientLuaTableToList('skill'))
    # fileList = os.listdir(config.get('projectRoot','sourceTablePath'))
    fileList = os.listdir(sourceTablePath)
    # fileList = ['timeArchiveItem.txt']
    # 这部分表的luatable格式有点不一样
    # profession的后端表有导出c_前缀的字段
    # itemWarning是编码问题
    # namePool的string字段有的行会带空格
    # mainChaptersNpcState----roguelikeOption是list中嵌套struct有bug待修复
    filterList = ['newbieRule.txt','soundUI.txt','profession.txt','itemWarning.txt','namePool.txt','mainChaptersNpcState.txt','mainChaptersObjSound.txt','roguelikeOption.txt']
    for fileName in fileList:
        # print(fileName)
        try:
            # 过滤包含中文和不是.txt后缀的文件
            if is_contain_chinese(fileName) or '.txt' not in fileName or fileName in filterList:
                continue
            compareList(fileName,sourceTableToList(sourceTablePath + '/' + fileName,'s_','c_'), clientLuaTableToList(fileName),'前端:')
            fieldNameList = []
            fieldTypeList = []
            tableList = []
            compareList(fileName,sourceTableToList(sourceTablePath + '/' + fileName,'c_','s_'), serverLuaTableToList(fileName),'后端:')
            fieldNameList = []
            fieldTypeList = []
            tableList = []
        except (UnicodeDecodeError,UnicodeError) as ue:
            print(fileName + ':文件编码问题打不开---------notepad可以改编码格式！！！')
            fieldNameList = []
            fieldTypeList = []
            tableList = []
        except FileNotFoundError as fe:
            msg = ''
            if serverLuaTablePath in str(fe).replace(r'\\','\\'):
                msg = '后端'
            else:
                msg = '前端'
            print(fileName + ':目录没有这个文件---------' + msg + '！！！')
            fieldNameList = []
            fieldTypeList = []
            tableList = []

    clientOnlyList = os.listdir(sourceTablePath + '/ClientOnly')
    for fileName in clientOnlyList:
        # 过滤包含中文和不是.txt后缀的文件
        if is_contain_chinese(fileName) or '.txt' not in fileName or fileName in filterList:
            continue
        compareList(fileName,sourceTableToList(sourceTablePath + '/' + 'ClientOnly/' + fileName,'s_','c_'),clientLuaTableToList(fileName),'前端:')
        fieldNameList = []
        fieldTypeList = []
        tableList = []

    serverOnlyList = os.listdir(sourceTablePath + '/ServerOnly')
    for fileName in serverOnlyList:
        # 过滤包含中文和不是.txt后缀的文件
        if is_contain_chinese(fileName) or '.txt' not in fileName or fileName in filterList:
            continue
        compareList(fileName,sourceTableToList(sourceTablePath + '/' + 'ServerOnly/' + fileName,'c_','s_'),serverLuaTableToList(fileName),'后端:')
        fieldNameList = []
        fieldTypeList = []
        tableList = []