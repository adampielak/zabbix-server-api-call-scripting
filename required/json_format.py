def print_json_format(data):
    default_indent = ' ' * 4
    initial_indent = ''
    def get_json_format(data, indent=initial_indent):
        my_str = ''
        strList = []
        current_indent = indent + default_indent
        if type(data) is dict:
            my_str += '{\n'
            for k, v in data.items():
                strList.append('{0}"{1}": {2}'.format(current_indent, k, get_json_format(v, current_indent)))
            my_str += ',\n'.join(strList)
            my_str += '\n{0}}}'.format(indent)
        elif type(data) is list:
            my_str += '[\n'
            for v in data:
                strList.append('{0}{1}'.format(current_indent, get_json_format(v, current_indent)))
            my_str += ',\n'.join(strList)
            my_str += '\n{0}]'.format(indent)
        elif type(data) is str:
            my_str += '"{0}"'.format(data)
        else:
            my_str += str(data)
        return my_str
    print(get_json_format(data))