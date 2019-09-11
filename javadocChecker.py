#!/usr/bin/env python
# coding: utf-8

# In[61]:


import os
import csv
import re
import traceback
import datetime

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

def get_error_message(type):
    msg = 'unknown error'
    if type == 1:
        msg = '少星號'
    elif type == 2:
        msg = '星號後少空白'
    elif type == 3:
        msg = 'Scriptlet錯誤'
    elif type == 4:
        msg = 'ID錯誤'
    elif type == 5:
        msg = '缺少第二行'
    elif type == 6:
        msg = '第二行冒號後少空白'
    elif type == 7:
        msg = '第二行少#號'
    elif type == 8:
        msg = '少<p>'
    elif type == 9:
        msg = '缺少第三行'
    elif type == 10:
        msg = '缺少第四行'
    elif type == 11:
        msg = '缺少空白行'
    return msg
        
    
def check_correct(java_path):
    global debugline
    debug = False
    tokens = re.split(r'[\\/]', java_path)
    print(tokens[-1])
    with open("Output.txt", "a") as text_file:
        text_file.write('\n<' + tokens[-1] + '>')
    begincount = 0
    endcount = 0
    spaceline = 0
    with open(java_path, 'r', encoding='utf-8') as f:
        f_content = f.readlines()
        parseStage = -1
        functionScript = None
        errormessage = ''
        ERR_COUUNT = 0
        ERR_SET = set()
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
                ERR_SET = set()
                continue
            elif inblock and '*/' in linestr:
                endcount += 1
                if parseStage > 0:
                    parseStage = 7
                continue
            elif inblock and not linestr.lstrip().startswith('*'):
                errormessage = append_message(errormessage, str(i+1) + ': ' + '1-' + get_error_message(1))
                ERR_SET.add(1)
            elif inblock and linestr.replace('*','').strip():
                if not str(line).lstrip().startswith('* '):
                    errormessage = append_message(errormessage,str(i+1) + ': ' + '2-' + get_error_message(2))
                    ERR_SET.add(2)

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
                            errormessage = append_message(errormessage, str(i+1) + ': ' + '3-' + get_error_message(3))
                            ERR_SET.add(3)
                        if tokens[3] != functionScript[1]:
                            errormessage = append_message(errormessage, str(i+1) + ': ' + '4-' + get_error_message(4))
                            ERR_SET.add(4)
                elif '@' in linestr:
                    pass
                else:
                    parseStage = 8
            if parseStage == 8:
                tokens = re.split(r'[ ]', linestr.lstrip())
                parseStage = -1
                if tokens[0] == 'public' and len(ERR_SET) > 0:
                    #print(functionScript[1]+ ':\n' + errormessage)
                    with open("Output.txt", "a") as text_file:
                        for err in ERR_SET:
                            text_file.write('\n' + functionScript[1] + ': ' + get_error_message(err))
                    
            if not inblock:
                continue
            if parseStage == 0:
                parseStage = 1
                functionScript = getFunctionScript(linestr)
                if not functionScript:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '5-' + get_error_message(5))
                    ERR_SET.add(5)
                elif linestr.find(': ') == -1:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '6-' + get_error_message(6))
                    ERR_SET.add(6)
                elif not functionScript[2]:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '7-' + get_error_message(7))
                    ERR_SET.add(7)
            elif parseStage == 1:
                if 'UsedByScriptlet' in linestr:
                    pass
                else:
                    parseStage = 2
                    if not linestr.replace('*', '').strip() == '<p>':
                        errormessage = append_message(errormessage, str(i+1) + ': ' + '8-' + get_error_message(8))
                        ERR_SET.add(8)
            elif parseStage == 2:
                parseStage = 3
                if not len(linestr.replace('*','').strip()) > 0:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '9-' + get_error_message(9))
                    ERR_SET.add(9)
            elif parseStage == 3:
                parseStage = 4
                if not len(linestr.replace('*','').strip()) > 0:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '10-' + get_error_message(10))
                    ERR_SET.add(10)
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
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '11-' + get_error_message(11))
                    ERR_SET.add(11)
                    spaceline = -1
        if len(ERR_SET) == 0:
            print('PASS')
            with open("Output.txt", "a") as text_file:
                text_file.write('\nPASS')
                
    
def check_comment(src_location, txn_assigned):  
    with open("Output.txt", "w") as text_file:
        text_file.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    for txn in txn_assigned:
        files = get_file_path(src_location, txn[0])
        print('\n' + txn[0] + ' ' + txn[1] + ':')
        with open("Output.txt", "w") as text_file:
            text_file.write('\n<' + tokens[-1] + '>')
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

