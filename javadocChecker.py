#!/usr/bin/env python
# coding: utf-8

import os
import csv
import re
import traceback
import datetime
import xml.etree.ElementTree as ET

debugline = 0
txn_to_debug = ''

def get_source_location():
    """determine where source code locate"""
    repo_path = ''
    txn_dirs = ["c://iisi/infinity-developer/repos/infinity-application-tfbnbts-transactions","d://iisi/infinity-developer/repos/infinity-application-tfbnbts-transactions","c://iisi/develop/infinity-developer/repos/infinity-application-tfbnbts-transactions","d://iisi/develop/infinity-developer/repos/infinity-application-tfbnbts-transactions","c://infinity/repos/infinity-application-tfbnbts-transactions"]
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
    if os.path.isdir(path):
        java_files = [f for f in os.listdir(path) if f.endswith('.java')]
        return java_files
    else:
        return None

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
    elif type == 12:
        msg = '程式空白拿掉註解'
    elif type == 13:
        msg = '第三行描述不符-前'
    elif type == 14:
        msg = '第三行描述不符-後'
    elif type == 15:
        msg = '@param缺描述'
    elif type == 16:
        msg = '@throws缺描述'    
    elif type == 17:
        msg = '@param/@throws拼字錯誤'  
    elif type == 18:
        msg = '@param/@throws錯誤'
    elif type == 19:
        msg = '@param/@throws描述錯誤'
    elif type == 20:
        msg = 'void不需要@return'
    elif type == 21:
        msg = '@return缺描述'
    elif type == 22:
        msg = 'UsedByScriptlet錯誤(或編輯器有多個CrossValidation模組)'
    return msg
        
def parseFunctionName(linestr):
    tokens = re.split(r'[(]', linestr)
    if len(tokens) > 0:
        tokens2 = re.split(r'[ ]', tokens[0])
        for token in reversed(tokens2):
            if token.strip():
                return token
    else:
        return None

def check_line3_rule(pstr, funScript):
    ecode = 0
    if funScript and False:
        if 'before' in funScript[1].lower() and 'CommentScriptlet' == funScript[0]:
            if not '前' in pstr:
                ecode = 13
        elif 'after' in funScript[1].lower() and 'CommentScriptlet' == funScript[0]:
            if not '後' in pstr:
                ecode = 14
    return ecode

def get_xml_location():
    paths = get_source_location()
    return paths[0] + '/infinity-module-tfbnbtsdesigns/src/main/design/flowEngine/flows/flows.jar'

def getXmlFile(txn):
    txn = txn.lower()
    if txn.endswith('java'):
        txn = txn[:-4]
    if not txn.endswith('.'):
        txn = txn + '.xml'
    else:
        txn = txn + 'xml'
    result = os.path.join(get_xml_location(), txn)
    if os.path.isfile(result):
        return result
    else:
        return None

def is_crossValidation(tree):
    for child in tree:
        if child.attrib['name'] == 'objectName' and child.attrib['value'] == 'MNM:type=com.iisigroup.infinity.modules.crossvalidation.CrossValidation,name=crossValidation':
            return True
    return False

def getRuleStatements(txn):
    rule_statement = ''
    xmlfile = getXmlFile(txn)
    if xmlfile:
        print('parse xml file: ' + xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for child in root:
            #if child.attrib['id'] == 'tx02004503.CrossValidation':
            if is_crossValidation(child):
                #print('shen for debug 1')
                for child2 in child:
                    #print(child2.tag, child2.attrib)
                    if child2.attrib['name'] == 'attributes':
                        #print('shen for debug 2')
                        for child3 in child2:
                            #print(child3.tag, child3.attrib)
                            if child3.tag == '{http://www.springframework.org/schema/beans}map':
                                #print('shen for debug 3')
                                for child4 in child3:
                                    if child4.attrib['key'] == 'rules':
                                        #print('shen for debug 4')
                                        for child5 in child4:
                                            #print('shen for debug 5')
                                            #print(child5.tag, child5.attrib)
                                            for child6 in child5:
                                                #print('shen for debug 6')
                                                #print(child6.tag, child6.attrib)
                                                for child7 in child6:
                                                    if child7.attrib['key'] == 'ruleStatements':
                                                        #print('shen for debug 7')
                                                        for child8 in child7:
                                                            #print(child8.text)
                                                            rule_statement = re.split(r'[\n]', child8.text)[0][12:]
    return rule_statement


def check_correct(java_path):
    global debugline
    debug = False
    tokens = re.split(r'[\\/]', java_path)
    print(tokens[-1])
    ruleStagement = getRuleStatements(tokens[-1])
    print('ruleStagement: ' + ruleStagement)
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
        isPass = True
        bufErrMsg = ''
        params_list = []
        params_return = None
        for i, line in enumerate(f_content):
            linestr = str(line)
            global txn_to_debug
            if txn_to_debug and txn_to_debug in java_path:
                print(str(parseStage) + ': ' + linestr)
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
                bufErrMsg = ''
                params_list = []
                params_return = None
                continue
            elif inblock and '*/' in linestr:
                endcount += 1
                if parseStage > 0 and parseStage < 8:
                    parseStage = 7
                elif parseStage > 8:
                    parseStage = -1
                    print('parseStage found error')
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
                elif 'Scriptlet' in linestr:
                    if functionScript:
                        tokens = re.split(r'[@("]', linestr)
                        if tokens[1] != functionScript[0]:
                            errormessage = append_message(errormessage, str(i+1) + ': ' + '3-' + get_error_message(3))
                            ERR_SET.add(3)
                        if tokens[3] != functionScript[1]:
                            print('id check: ' + tokens[3])
                            print('id chec2: ' + functionScript[1])
                            errormessage = append_message(errormessage, str(i+1) + ': ' + '4-' + get_error_message(4))
                            ERR_SET.add(4)
                elif '@' in linestr:
                    pass
                else:
                    parseStage = 8
            if parseStage == 8:
                #parseStage = -1
                #check if params are aligned with javadoc description
                tokens = re.split(r'[()]', linestr.strip())
                if len(tokens) > 2:
                    FunctioinParameters = tokens[1]
                    #remove parameter with <>, like Map<String, String>
                    while FunctioinParameters.find('<') > 0:
                        rm_from = FunctioinParameters.find('<')
                        rm_to = FunctioinParameters.find('>')
                        FunctioinParameters = FunctioinParameters[:rm_from] + FunctioinParameters[rm_to+1:]
                    para_tokens = re.split(r'[,]', FunctioinParameters)
                    isVoidRetrun = True if 'void' in tokens[0] else False
                    if not 'throws' in tokens[2]:
                        throws_tokens = []
                    else:
                        throws_tokens = re.split(r'[,]', tokens[2][tokens[2].find('throws')+6:tokens[2].find('{')])
                    if len(params_list) != len(para_tokens) + len(throws_tokens):
                        print(params_list)
                        print(para_tokens)
                        print(throws_tokens)
                        print('shen 0')
                        ERR_SET.add(18)
                    else:
                        for ip, para in enumerate(para_tokens):
                            para_token = re.split(r'[ ]', para.strip())
                            if para_token[-1].strip() != params_list[ip][0]:
                                ERR_SET.add(18)
                                print('shen 1')
                            elif para_token[0].strip() == 'TfbNbtsFacadeProxy' and params_list[ip][1] != '流程Facade':
                                ERR_SET.add(18)
                                print('shen 2')
                                print(params_list[ip][1])
                            elif para_token[0].strip() == 'FlowContext' and params_list[ip][0] == 'c' and params_list[ip][1] != '交易內文':
                                ERR_SET.add(18)
                                print('shen 3')
                                print(params_list[ip][1])
                            elif para_token[0].strip() == 'Notification' and params_list[ip][1] != '通知':
                                ERR_SET.add(18)
                                print('shen 4')
                                print(params_list[ip][1])
                            elif para_token[0].strip() == 'FlowContext' and params_list[ip][0] == 'cs' and params_list[ip][1] != '來源交易內文':
                                ERR_SET.add(18)
                                print('shen 5')
                                print(params_list[ip][1])
                            elif para_token[0].strip() == 'FlowContext' and params_list[ip][0] == 'ct' and params_list[ip][1] != '目的交易內文':
                                ERR_SET.add(18)
                                print('shen 6')
                        for it, throw in enumerate(throws_tokens):
                            if throw.strip() != params_list[len(para_tokens) + it][0]:
                                ERR_SET.add(18)
                                print('shen 7')
                            elif params_list[len(para_tokens) + it][1] != '例外錯誤':
                                ERR_SET.add(18)
                                print('shen 8')
                        if isVoidRetrun and params_return:
                            ERR_SET.add(20)
                else:
                    if len(params_list) > 0:
                        ERR_SET.add(18)
                        print('shen 9')
                    
                tokens = re.split(r'[ ]', linestr.lstrip())
                if tokens[0] == 'public' and len(ERR_SET) > 0:
                    parseStage = 9
                    #print(functionScript[1]+ ':\n' + errormessage)
                    #with open("Output.txt", "a") as text_file:
                    for err in ERR_SET:
                        #text_file.write('\n' + functionScript[1] + ': ' + get_error_message(err))
                        if parseFunctionName(linestr):
                            bufErrMsg += '\n' + parseFunctionName(linestr) + ': ' + get_error_message(err)
                        else:
                            bufErrMsg += '\n' + functionScript[1] + ': ' + get_error_message(err)
                    isPass = False
                elif tokens[0] == 'public':
                    parseStage = 9
                else:
                    parseStage = -1
            elif parseStage == 9:
                parseStage = -1
                linep = linestr[:linestr.find('//')].strip()
                if linep.startswith('}'):
                    isPass = False
                    bufErrMsg = '\n' + functionScript[1] + ': ' + get_error_message(12)
                    with open("Output.txt", "a") as text_file:
                        text_file.write(bufErrMsg)
                elif linep:
                    with open("Output.txt", "a") as text_file:
                        text_file.write(bufErrMsg)
                else:
                    parseStage = 9
                    
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
                    if not linestr[linestr.find(':') + 1:].strip() == ruleStagement.strip():
                        print('debug check: "' + linestr[linestr.find(':') + 1:].strip() + '"')
                        print('debug chek2: "' + ruleStagement.strip() + '"')
                        errormessage = append_message(errormessage, str(i + 1) + ': ' + '22-' + get_error_message(22))
                        ERR_SET.add(22)
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
                errcode = check_line3_rule(linestr, functionScript)
                if errcode > 0:
                    ERR_SET.add(errcode)
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
            if parseStage == 6:
                if spaceline == 0:
                    errormessage = append_message(errormessage, str(i+1) + ': ' + '11-' + get_error_message(11))
                    ERR_SET.add(11)
                    spaceline = -1
                if functionScript and functionScript[0] == 'Method':
                    # if '@' in linestr:
                    #     continue
                    #print(str(i+1) + ': ' + functionScript[1] + ' check required')
                    if not '@' in linestr:
                        if tokens[3] != functionScript[1]:
                            print('id check: ' + tokens[3])
                            print('id chec2: ' + functionScript[1])
                            errormessage = append_message(errormessage, str(i+1) + ': ' + '4-' + get_error_message(4))
                            ERR_SET.add(4)
                #handle @param and @throws
                if '@param' in linestr or '@throws' in linestr:
                    tokens = re.split(r'[ ]', linestr.strip())
                    if len(tokens) < 4:
                        if '@param' == tokens[1].strip():
                            ERR_SET.add(15)
                        elif '@throws' == tokens[1].strip():
                            ERR_SET.add(16)
                        else:
                            ERR_SET.add(17)
                    else:
                        params_list.append((tokens[2], tokens[3]))
                elif '@return' in linestr:
                    tokens = re.split(r'[ ]', linestr.strip())
                    if len(tokens) < 3:
                        if '@return' == tokens[1].strip():
                            ERR_SET.add(21)
                        else:
                            ERR_SET.add(17)
                    else:
                        params_return = tokens[2]

        if isPass:
            print('PASS')
            with open("Output.txt", "a") as text_file:
                text_file.write('\nPASS')

def check_comment(src_location, txn_assigned):  
    with open("Output.txt", "w") as text_file:
        text_file.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    for txn in txn_assigned:
        files = get_file_path(src_location, txn[0])
        print('\n' + txn[0] + ' ' + txn[1] + ':')
        with open("Output.txt", "a") as text_file:
            text_file.write('\n\n<' + txn[1] + '>' + ' : ' + txn[0])
            if not files:
                text_file.write('\n[WARNNING] No folder found: ' + txn[0])
        if files:
            for file in files:
                check_correct(os.path.join(src_location[1], txn[0], file))

def writeOutputToCsv(outfilename, csvfilename):
    with open(csvfilename, 'w', newline='') as csvfile:
        fieldnames = ['txn', 'owner', 'result']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        txn = ''
        owner = ''
        result = ''
        stage = 0
        with open(outfilename, "r") as result_file:
            f_content = result_file.readlines()
            for line in f_content:
                strline = str(line).strip()
                if stage == 0:
                    tokens = re.split(r'[:]', strline)
                    if len(tokens) < 2:
                        continue
                    towner = tokens[0].strip()
                    txn = tokens[1].strip()
                    if towner.startswith('<') and towner.endswith('>'):
                        owner = towner[1:-1]
                        stage = 1
                elif stage == 1:
                    if strline:
                        result = result + strline + '\n'
                    else:
                        stage = 0
                        writer.writerow({'txn': txn, 'owner': owner, 'result': result})
                        owner = ''
                        result = ''
                        txn = ''
            if txn:
                writer.writerow({'txn': txn, 'owner': owner, 'result': result})

def main():
    global debugline
    src_dirs = get_source_location()
    txn_to_check = get_check_txn()
    try:
        check_comment(src_dirs, txn_to_check)
    except Exception as e:
        print('error at ' + str(debugline))
        traceback.print_exc()
    csvfile = datetime.datetime.now().strftime("%Y%m%d%H%M") + '.csv'
    print(csvfile)
    writeOutputToCsv('Output.txt', csvfile)

if __name__ == '__main__':
    try:
        main()
    finally:
        print('press Enter to continue...')
        #input()
