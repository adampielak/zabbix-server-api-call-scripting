from json_format import print_json_format

def logging_decorator(beforeLog, afterLog, params=None, json_format_result=True):
    def decorator_function(original_function):
        def wrapper_function(*args, **kwargs):
            print(beforeLog)
            if params:
                print_json_format(params)
            result = original_function(*args, **kwargs)
            print(afterLog)
            if json_format_result:
                print_json_format(result)
            print('\n')
            return result
        return wrapper_function
    return decorator_function