import xml.etree.ElementTree as et
# 递归遍历xml文件
def walkData(root_node, level, result_list):
    temp_list = [level, root_node.tag, root_node.attrib]
    result_list.append(temp_list)
    
    children_node = list(root_node)
    if len(children_node) == 0:
        return
    for child in children_node:
        walkData(child, level+1, result_list)
    return

def getXmlData(file_name):
    level = 1
    result_list = []
    root = et.parse(file_name).getroot()
    walkData(root, level, result_list)
    return result_list
