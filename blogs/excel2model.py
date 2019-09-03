from django.apps import apps


def excel_into_model(appname, model_name, excel_file):
    # tmp[7].verbose_name.__str__()
    try:
        appname_ = apps.get_model(appname, model_name)
        fields = appname_._meta.fields
        # 导入model,动态导入
        exec('from %s.models import %s' % (appname, model_name))
    except:
        print('model_name and appname is not exist')
    field_name = []
    # 只导入第一个sheet中的数据
    table = excel_file.sheet_by_index(0)
    nrows = table.nrows
    table_header = table.row_values(0)
    for cell in table_header:
        for name in fields:
            if cell in name.verbose_name.__str__():
                field_name.append(name.name)
    if 'add_time' in field_name:
        field_name.remove('add_time')
    for x in range(1, nrows):
        # 行的数据,创建对象,进行报错数据
        exec('obj' + '=%s()' % model_name)
        print(len(field_name))
        for y in range(len(field_name)):
            exec('obj.%s' % field_name[y] + '="%s"' % (table.cell_value(x, y)))
        exec('obj.save()')


def createInstance(module_name, class_name, *args, **kwargs):
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj


def excel_into_obj_list(appname, model_name, excel_file):
    # tmp[7].verbose_name.__str__()
    try:
        appname_ = apps.get_model(appname, model_name)
        fields = appname_._meta.fields
        # 导入model,动态导入
        exec('from %s.models import %s' % (appname, model_name))
    except:
        print('model_name and appname is not exist')
    field_name = []
    # 只导入第一个sheet中的数据
    table = excel_file.sheet_by_index(0)
    nrows = table.nrows
    table_header = table.row_values(0)
    for cell in table_header:
        for name in fields:
            if cell in name.verbose_name.__str__():
                field_name.append(name.name)
    if 'add_time' in field_name:
        field_name.remove('add_time')
    model_list = []
    for x in range(1, nrows):
        # 行的数据,创建对象,进行报错数据
        obj = createInstance("%s.models" % appname, model_name)
        for y in range(len(field_name)):
            obj.__setattr__(field_name[y], table.cell_value(x, y))
        model_list.append(obj)
    return model_list


def excel_into_json_list(appname, model_name, excel_file):
    # tmp[7].verbose_name.__str__()
    try:
        appname_ = apps.get_model(appname, model_name)
        fields = appname_._meta.fields
        # 导入model,动态导入
        exec('from %s.models import %s' % (appname, model_name))
    except:
        print('model_name and appname is not exist')
    field_name = []
    # 只导入第一个sheet中的数据
    table = excel_file.sheet_by_index(0)
    nrows = table.nrows
    table_header = table.row_values(0)
    for cell in table_header:
        for name in fields:
            if cell in name.verbose_name.__str__():
                field_name.append(name.name)
    if 'add_time' in field_name:
        field_name.remove('add_time')
    json_list = []
    for x in range(1, nrows):
        # 行的数据,创建对象,进行报错数据
        # obj = createInstance("%s.models" % appname, model_name)
        js = {}
        for y in range(len(field_name)):
            js[field_name[y]]=table.cell_value(x, y)
        json_list.append(js)
    return json_list