import os
import json
import datetime
import sys

def add(matrix,x,y,z):
    # -- index X
    if not 'x' in matrix:
        matrix['x'] = []
    if not x in matrix['x']:
        matrix['x'].append(x)

    # -- index Y
    if not 'y' in matrix:
        matrix['y'] = []
    if not y in matrix['y']:
        matrix['y'].append(y)

    # -- index z
    if not 'z' in matrix:
        matrix['z'] = {}

    if not x in matrix['z']:
        matrix['z'][x] = {}
    
    matrix['z'][x][y] = z

def render_markdown(matrix):
    matrix['x'].sort()
    matrix['y'].sort()

    out = "||**" + "**|**".join(matrix['x']) + "**|\n"
    out += "|--" * (len(matrix['x']) + 1) + "|\n"
    for y in matrix['y']:
        out += f"|**{y}**|"
        for x in matrix['x']:
            out += f"{matrix['z'][x].get(y,'')}|"
        out += "\n"

    return out
   
def WriteJSONFile(data,file):

    with open(file,'wt') as J:
        J.write(json.dumps(data , indent=4))
            
def ReadJSONFile(file,WithErrors = False):
    if WithErrors:
        with open(file,'rt') as J:
            return json.load(J)
    else:
        try:
            with open(file,'rt') as J:
                return json.load(J)
        except:
            print(' ** FAILED -- defaulting to empty **')
            return {}

def get_control_summary(data):
    result = {}
    for x in data['groups']:
        for y in x['groups']:
            for z in y['groups']:
                for a in z['controls']:
                    result[a['control_id']] = a['summary']

    return result       
    
def get_control_list(data):
    result = {}

    for x in data['groups']:
        for y in x['groups']:
            for z in y['groups']:
                for a in z['controls']:
                    result[a['control_id']] = {
                        'title' : a['title'],
                        'description' : a['description'],
                        'summary' : a['summary'],
                        'results'   : a['results']
                    }

    return result   

def anchor(text):
    return text.lower().replace(' ','-').replace('%','').replace('(','').replace(')','').replace('---','-').replace('--','-')
    
# =======================================================================================================================

def main(json_file,history_file,markdown_file):
    print('parameters..')
    print(f'1 - json_file = {json_file}')
    print(f'2 - history_file = {history_file}')
    print(f'3 - markdown file - {markdown_file}')
    
    history = ReadJSONFile(history_file,False)
    
    # -- get this month's slot
    slot = "{:04d}-{:02d}".format(datetime.datetime.today().year,datetime.datetime.today().month)
    if not slot in history:
        history[slot] = {}
    
    # == Get the file that was sent to S3
    data = ReadJSONFile(json_file,True)
    
    # == read through the data, and write the history back
    X = get_control_summary(data)
    for control in X:
        history[slot][control] = X[control]
        
    # == now we generate the markdown file
    list_of_controls = get_control_list(data)
    
    ct_index = {}
    for x in list_of_controls:
        title = list_of_controls[x]['title']
        for slot in history:
            if x in history[slot]:
                if history[slot][x]['ok'] + history[slot][x]['alarm'] > 0:
                    pct = history[slot][x]['ok'] / ( history[slot][x]['ok'] + history[slot][x]['alarm']) * 100.0
                else:
                    pct = 0

                a = anchor(title)
                add(ct_index,slot,f"[{title}](#{a})",f"{pct:.2f}%")
    
    # == produce the output markdown file

    markdown = '# Mantel Group ISMS Security Dashboard\n'
    markdown += '\n'
    markdown += '## Summary\n'
    markdown += '\n'
    markdown += render_markdown(ct_index)

    markdown += '\n'
    for x in list_of_controls:
        title = list_of_controls[x]['title']
        description = list_of_controls[x]['description']
        summary = list_of_controls[x]['summary']

        markdown += f'## {title}\n'
        markdown += '\n'
        markdown += description
        markdown += '\n'

        markdown += '|**OK &#9989;**|**Skip &#8680;**|**Info &#8505;**|**Alarm &#10060;**|**Error &#10071;**|**Total**|\n'
        markdown += '|--|--|--|--|--|--|\n'
        total = summary['ok'] + summary['skip'] + summary['info'] + summary['alarm'] + summary['error']
        markdown += f"|{summary['ok']}|{summary['skip']}|{summary['info']}|{summary['alarm']}|{summary['error']}|{total}|\n"
        markdown += '\n'

        markdown += '### Detail\n'
        markdown += '\n'

        status = {
            'ok' : '&#9989;',
            'skip' : '&#8680;',
            'alarm' : '&#10060;'
        }

        if list_of_controls[x]['results'] != None:
            markdown += '|**Status**|**Resource**|**Reason**|\n'
            markdown += '|--|--|--|\n'

            for i in list_of_controls[x]['results']:
                if i['status'] != 'ok':
                    markdown += f"|{status[i['status']]}|{i['resource']}|{i['reason']}\n"

            markdown += '\n'

    
    # == write the history file back
    WriteJSONFile(history,history_file)

    # == write the markdown file
    with open(markdown_file,'wt') as m:
        m.write(markdown)

       
    
main(sys.argv[1],sys.argv[2],sys.argv[3])