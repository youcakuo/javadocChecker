#!/usr/bin/env python
# coding: utf-8

# In[61]:


import os
import csv
import re
import traceback

debugline = 0

def get_source_location():
    repo_path = ''
    txn_dirs = ["c://iisi/infinity-developer/repos/infinity-application-tfbnbts-transactions","d://iisi/infinity-developer/repos/infinity-application-tfbnbts-transactions","c://iisi/develop/infinity-developer/repos/infinity-application-tfbnbts-transactions","d://iisi/develop/infinity-developer/repos/infinity-application-tfbnbts-transactions"]
    for txn_dir in txn_dirs:
            if os.path.isdir(txn_dir):
                repo_path = txn_dir
                break
    if repo_path:
        txn_path = repo_path + '/infinity-module-tfbnbtsdesigns/src/main/java/design/scriptlet/flow'
    else:
        txn_path = ''
    return (repo_path, txn_path)
    
def get_check_txn():
    txn_list = []
    with open('check.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            txn = row['txn']
            owner = row['owner']
            txn_list.append((txn, owner))
    return txn_list

def get_file_path(location, txn):
    path = os.path.join(location[1], txn)
    java_files = [f for f in os.listdir(path) if f.endswith('.java')]
    return java_files

def getFunctionScript(str):
    tokens = re.split( r'[*#:]', str )
    if len(tokens) >= 4:
        return (tokens[2].strip(), tokens[3].strip(),True)
    else:
        tokens = re.split( r'[*:]', str )
        if len(tokens) >= 3:
            return (tokens[1].strip(), tokens[2].strip(),False)
        else:
            return None

def append_message(msg, apd):
    if not msg:
        return apd
    else:
        return msg + '\n' + apd
        
def check_correct(java_path):
    global debugline
    debug = False
    #print(java_path)
    tokens = re.split(r'[\\/]', java_path)
    print(tokens[-1])
    begincount = 0
    endcount = 0
    spaceline = 0
    with open(java_path, 'r', encoding='utf-8') as f:
        f_content = f.readlines()
        parseStage = -1
        functionScript = None
        errormessage = ''
        ERR_COUUNT = 0
        for i, line in enumerate(f_content):
            linestr = str(line)
            debugline = i
            if linestr.lstrip().startswith('//'):
                continue
            inblock = True if endcount < begincount else False
            if linestr.lstrip().startswith('/**') and linestr.rstrip().endswith('/**'):
                begincount += 1
                spaceline = 0
                parseStage = 0
                functionScript = None
                errormessage = ''
                continue
            elif inblock and '*/' in linestr:
                endcount += 1
                if parseStage > 0:
                    parseStage = 7
                continue
            elif inblock and not linestr.lstrip().startswith('*'):
                #print(str(i+1) + ': ' + 'wrong format1 : star is required')
                #errormessage = errormessage + str(i+1) + ': ' + 'wrong format3 : star is required\n'
                errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong format3 : 少星號')
            elif inblock and linestr.replace('*','').strip():
                if not str(line).lstrip().startswith('* '):
                    #print(str(i+1) + ': ' + 'wrong format4 : need one space before comment')
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong format2 : need one space before comment\n'
                    errormessage = append_message(errormessage,str(i+1) + ': ' + 'wrong format2 : 星號後少空白')

            if parseStage == 7:
                if not functionScript:
                    parseStage = -1
                    continue
                if functionScript[0] == 'Method':
                    parseStage = -1
                    print(str(i+1) + ': ' + functionScript[1] + ' check required')
                if 'Scriptlet' in linestr:
                    if functionScript:
                        tokens = re.split(r'[@("]', linestr)
                        if tokens[1] != functionScript[0]:
                            #print(str(i+1) + ': ' + 'wrong fromat8 : Scriptlet type error')
                            #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat10 : Scriptlet type error\n'
                            errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat10 : Scriptlet錯誤')
                        if tokens[3] != functionScript[1]:
                            #print(str(i+1) + ': ' + 'wrong fromat9 : id name is error')
                            #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat11 : id name is error\n'
                            errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat11 : ID錯誤')
                elif '@' in linestr:
                    pass
                else:
                    parseStage = 8
            if parseStage == 8:
                tokens = re.split(r'[ ]', linestr.lstrip())
                parseStage = -1
                if tokens[0] == 'public' and errormessage:
                    print(functionScript[1]+ ':\n' + errormessage)   
                    ERR_COUUNT += 1
                    
            if not inblock:
                continue
            if parseStage == 0:
                parseStage = 1
                functionScript = getFunctionScript(linestr)
                if not functionScript:
                    #print(str(i+1) + ': ' + 'wrong fromat5 : error line2')
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat3 : error line2\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat3 : 缺少第二行')
                elif linestr.find(': ') == -1:
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat3 : error line2\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat3 : 第二行冒號後少空白')
                elif not functionScript[2]:
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat3 : error line2\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat3 : 第二行少#號')
            elif parseStage == 1:
                if 'UsedByScriptlet' in linestr:
                    #print(str(i+1) + ': ' + '[shen] UsedByScriptlet found')
                    pass
                else:
                    parseStage = 2
                    if not linestr.replace('*', '').strip() == '<p>':
                        #print(str(i+1) + ': ' + 'wrong fromat4 : <p> is required')
                        #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat6 : <p> is required\n'
                        errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat6 : 少<p> ')
            elif parseStage == 2:
                parseStage = 3
                if not len(linestr.replace('*','').strip()) > 0:
                    #print(str(i+1) + ': ' + 'wrong fromat5 : <p> line3 is required')
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat7 : <p> line3 is required\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat7 : <p> 缺少第三行')
            elif parseStage == 3:
                parseStage = 4
                if not len(linestr.replace('*','').strip()) > 0:
                    #print(str(i+1) + ': ' + 'wrong fromat6 : <p> line4 is required')
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat8 : <p> line4 is required\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat8 : 缺少第四行')
            elif parseStage == 4:
                if len(linestr.replace('*','').strip()) == 0:
                    spaceline += 1
                    parseStage = 5
            elif parseStage == 5:
                if len(linestr.replace('*','').strip()) == 0:
                    spaceline += 1
                    continue
                else:
                    parseStage = 6
            elif parseStage == 6:
                if spaceline == 0:
                    #print(str(i+1) + ': ' + 'wrong fromat9 : one empty line required after line 4')
                    #errormessage = errormessage + str(i+1) + ': ' + 'wrong fromat7 : one empty line required after line 4\n'
                    errormessage = append_message(errormessage, str(i+1) + ': ' + 'wrong fromat7 : 缺少空白行')
                    spaceline = -1
        if ERR_COUUNT == 0:
            print('PASS')
                
    
def check_comment(src_location, txn_assigned):  
    for txn in txn_assigned:
        files = get_file_path(src_location, txn[0])
        print('\n' + txn[0] + ' ' + txn[1] + ':')
        for file in files:
            check_correct(os.path.join(src_location[1], txn[0], file))

def main():
    global debugline
    src_dirs = get_source_location()
    txn_to_check = get_check_txn()
    try:
        check_comment(src_dirs, txn_to_check)
    except Exception as e:
        print('error at ' + str(debugline))
        traceback.print_exc()
if __name__ == '__main__':
    try:
        main()
    finally:
        print('press Enter to continue...')
        #input()

