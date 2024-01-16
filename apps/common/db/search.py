# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： search.py
    @date：2023/10/7 18:20
    @desc:
"""
from typing import Dict, Any

from django.db import DEFAULT_DB_ALIAS, models, connections
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


def generate_sql_by_query_dict(queryset_dict: Dict[str, QuerySet], select_string: str,
                               field_replace_dict: None | Dict[str, Dict[str, str]] = None, with_table_name=False):
    """
    生成 查询sql
    :param with_table_name:
    :param queryset_dict: 多条件 查询条件
    :param select_string: 查询sql
    :param field_replace_dict:  需要替换的查询字段,一般不需要传入如果有特殊的需要传入
    :return: sql:需要查询的sql params: sql 参数
    """

    params_dict: Dict[int, Any] = {}
    result_params = []
    for key in queryset_dict.keys():
        value = queryset_dict.get(key)
        sql, params = compiler_queryset(value, None if field_replace_dict is None else field_replace_dict.get(key),
                                        with_table_name)
        params_dict = {**params_dict, select_string.index("${" + key + "}"): params}
        select_string = select_string.replace("${" + key + "}", sql)

    for key in sorted(list(params_dict.keys())):
        result_params = [*result_params, *params_dict.get(key)]
    return select_string, result_params


def generate_sql_by_query(queryset: QuerySet, select_string: str,
                          field_replace_dict: None | Dict[str, str] = None, with_table_name=False):
    """
    生成 查询sql
    :param queryset:            查询条件
    :param select_string:       原始sql
    :param field_replace_dict:  需要替换的查询字段,一般不需要传入如果有特殊的需要传入
    :return:  sql:需要查询的sql params: sql 参数
    """
    sql, params = compiler_queryset(queryset, field_replace_dict, with_table_name)
    return select_string + " " + sql, params


def compiler_queryset(queryset: QuerySet, field_replace_dict: None | Dict[str, str] = None, with_table_name=False):
    """
    解析 queryset查询对象
    :param with_table_name:
    :param queryset:            查询对象
    :param field_replace_dict:  需要替换的查询字段,一般不需要传入如果有特殊的需要传入
    :return: sql:需要查询的sql params: sql 参数
    """
    q = queryset.query
    compiler = q.get_compiler(DEFAULT_DB_ALIAS)
    if field_replace_dict is None:
        field_replace_dict = get_field_replace_dict(queryset)
    app_sql_compiler = AppSQLCompiler(q, using=DEFAULT_DB_ALIAS, connection=compiler.connection,
                                      field_replace_dict=field_replace_dict)
    sql, params = app_sql_compiler.get_query_str(with_table_name=with_table_name)
    return sql, params


def native_search(queryset: QuerySet | Dict[str, QuerySet], select_string: str,
                  field_replace_dict: None | Dict[str, Dict[str, str]] | Dict[str, str] = None,
                  with_search_one=False, with_table_name=False):
    """
    复杂查询
    :param with_table_name:     生成sql是否包含表名
    :param queryset:            查询条件构造器
    :param select_string:       查询前缀 不包括 where limit 等信息
    :param field_replace_dict:  需要替换的字段
    :param with_search_one:     查询
    :return: 查询结果
    """
    if isinstance(queryset, Dict):
        exec_sql, exec_params = generate_sql_by_query_dict(queryset, select_string, field_replace_dict, with_table_name)
    else:
        exec_sql, exec_params = generate_sql_by_query(queryset, select_string, field_replace_dict, with_table_name)
    if with_search_one:
        return select_one(exec_sql, exec_params)
    else:
        return select_list(exec_sql, exec_params)


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


def native_page_search(current_page: int, page_size: int, queryset: QuerySet | Dict[str, QuerySet], select_string: str,
                       field_replace_dict=None,
                       post_records_handler=lambda r: r,
                       with_table_name=False):
    """
    复杂分页查询
    :param with_table_name:
    :param current_page:          当前页
    :param page_size:             每页大小
    :param queryset:              查询条件
    :param select_string:         查询
    :param field_replace_dict:    特殊字段替换
    :param post_records_handler:  数据row处理器
    :return: 分页结果
    """
    if isinstance(queryset, Dict):
        exec_sql, exec_params = generate_sql_by_query_dict(queryset, select_string, field_replace_dict, with_table_name)
    else:
        exec_sql, exec_params = generate_sql_by_query(queryset, select_string, field_replace_dict, with_table_name)
    total_sql = "SELECT \"count\"(*) FROM (%s) temp" % exec_sql
    total = select_one(total_sql, exec_params)
    limit_sql = connections[DEFAULT_DB_ALIAS].ops.limit_offset_sql(
        ((current_page - 1) * page_size), (current_page * page_size)
    )
    page_sql = exec_sql + " " + limit_sql
    result = select_list(page_sql, exec_params)
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
