import json
import os

def get_index(obj_list, field, value):
    for i in range(len(obj_list)):
        if obj_list[i][field] == value:
            return i
    return None

def get_num_to_str(num,point=3,pType="float"):
    if point == 0:
        num = int(num)
    return str(format(round(num,point),','))

def write_file(path, file_name, data, override=False):
    if os.path.isdir(path) != True:
        os.makedirs(path)
    if override:
        mode = 'w'
    else:
        mode = 'a'
    w = open(path + file_name,mode, encoding='utf-8')
    w.write(data+'\n')
    w.close()

def read_file(file_name):
    r = open(file_name, mode='rt', encoding='utf-8')
    result = r.read()
    r.close()
    return result

def write_json(path, file_name, data, override=False):
    if os.path.isdir(path) != True:
        os.makedirs(path)
    if override:
        mode = 'w'
    else:
        mode = 'a'
    w = open(path + file_name,mode, encoding='utf-8')
    json.dump(data, w)
    w.close()

def read_json(file_name):
    try:
        r = open(file_name, mode='rt', encoding='utf-8')
        contents = r.read()
        result = json.loads(contents)
        r.close()
        return result
    except:
        return None