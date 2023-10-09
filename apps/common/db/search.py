# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： search.py
    @date：2023/10/7 18:20
    @desc:
"""

from django.db import DEFAULT_DB_ALIAS, models
from django.db.models import QuerySet

from common.db.compiler import AppSQLCompiler
from common.db.sql_execute import select_one, select_list
from common.response.result import Page


def get_dynamics_model(attr: dict, table_name='dynamics'):
    """
    获取一个动态的django模型
    :param attr:       模型字段
    :param table_name: 表名
    :return: django 模型
    """
    attributes = {
        "__module__": "dataset.models",
        "Meta": type("Meta", (), {'db_table': table_name}),
        **attr
    }
    return type('Dynamics', (models.Model,), attributes)


def native_search(queryset: QuerySet, select_string: str,
                  field_replace_dict=None,
                  with_search_one=False):
    """
    复杂查询
    :param queryset:            查询条件构造器
    :param select_string:       查询前缀 不包括 where limit 等信息
    :param field_replace_dict:  需要替换的字段
    :param with_search_one:     查询
    :return: 查询结果
    """
    if field_replace_dict is None:
        field_replace_dict = get_field_replace_dict(queryset)
    q = queryset.query
    compiler = q.get_compiler(DEFAULT_DB_ALIAS)
    app_sql_compiler = AppSQLCompiler(q, using=DEFAULT_DB_ALIAS, connection=compiler.connection,
                                      field_replace_dict=field_replace_dict)
    sql, params = app_sql_compiler.get_query_str(with_table_name=False)
    if with_search_one:
        return select_one(select_string + " " +
                          sql, params)
    else:
        return select_list(select_string + " " +
                           sql, params)


def page_search(current_page: int, page_size: int, queryset: QuerySet, post_records_handler):
    """
    分页查询
    :param current_page:         当前页
    :param page_size:            每页大小
    :param queryset:             查询条件
    :param post_records_handler: 数据处理器
    :return:  分页结果
    """
    total = QuerySet(query=queryset.query.clone(), model=queryset.model).count()
    result = queryset.all()[((current_page - 1) * page_size):(current_page * page_size)]
    return Page(total, list(map(post_records_handler, result)), current_page, page_size)


def native_page_search(current_page: int, page_size: int, queryset: QuerySet, select_string: str,
                       field_replace_dict=None,
                       post_records_handler=lambda r: r):
    """
    复杂分页查询
    :param current_page:          当前页
    :param page_size:             每页大小
    :param queryset:              查询条件
    :param select_string:         查询
    :param field_replace_dict:    特殊字段替换
    :param post_records_handler:  数据row处理器
    :return: 分页结果
    """
    if field_replace_dict is None:
        field_replace_dict = get_field_replace_dict(queryset)
    q = queryset.query
    compiler = q.get_compiler(DEFAULT_DB_ALIAS)
    app_sql_compiler = AppSQLCompiler(q, using=DEFAULT_DB_ALIAS, connection=compiler.connection,
                                      field_replace_dict=field_replace_dict)
    page_sql, params = app_sql_compiler.get_query_str(with_table_name=False)
    total_sql = "SELECT \"count\"(*) FROM (%s) temp" % (select_string + " " + page_sql)
    total = select_one(total_sql, params)
    q.set_limits(((current_page - 1) * page_size), (current_page * page_size))
    app_sql_compiler = AppSQLCompiler(q, using=DEFAULT_DB_ALIAS, connection=compiler.connection,
                                      field_replace_dict=field_replace_dict)
    page_sql, params = app_sql_compiler.get_query_str(with_table_name=False)
    result = select_list(select_string + " " + page_sql, params)
    return Page(total.get("count"), list(map(post_records_handler, result)), current_page, page_size)


def get_field_replace_dict(queryset: QuerySet):
    """
    获取需要替换的字段 默认 “xxx.xxx”需要被替换成 “xxx”."xxx"
    :param queryset: 查询对象
    :return: 需要替换的字典
    """
    result = {}
    for field in queryset.model._meta.local_fields:
        if field.attname.__contains__("."):
            replace_field = to_replace_field(field.attname)
            result.__setitem__('"' + field.attname + '"', replace_field)
    return result


def to_replace_field(field: str):
    """
    将field 转换为 需要替换的field  “xxx.xxx”需要被替换成 “xxx”."xxx" 只替换 field包含.的字段
    :param field: django field字段
    :return: 替换字段
    """
    split_field = field.split(".")
    return ".".join(list(map(lambda sf: '"' + sf + '"', split_field)))
