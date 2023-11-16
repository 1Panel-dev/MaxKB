# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： compiler.py
    @date：2023/10/7 10:53
    @desc:
"""

from django.core.exceptions import EmptyResultSet
from django.db import NotSupportedError
from django.db.models.sql.compiler import SQLCompiler


class AppSQLCompiler(SQLCompiler):
    def __init__(self, query, connection, using, elide_empty=True, field_replace_dict=None):
        super().__init__(query, connection, using, elide_empty)
        if field_replace_dict is None:
            field_replace_dict = {}
        self.field_replace_dict = field_replace_dict

    def get_query_str(self, with_limits=True, with_table_name=False):
        refcounts_before = self.query.alias_refcount.copy()
        try:
            extra_select, order_by, group_by = self.pre_sql_setup()
            for_update_part = None
            # Is a LIMIT/OFFSET clause needed?
            with_limit_offset = with_limits and (
                    self.query.high_mark is not None or self.query.low_mark
            )
            combinator = self.query.combinator
            features = self.connection.features
            if combinator:
                if not getattr(features, "supports_select_{}".format(combinator)):
                    raise NotSupportedError(
                        "{} is not supported on this database backend.".format(
                            combinator
                        )
                    )
                result, params = self.get_combinator_sql(
                    combinator, self.query.combinator_all
                )
            else:
                distinct_fields, distinct_params = self.get_distinct()
                try:
                    where, w_params = (
                        self.compile(self.where) if self.where is not None else ("", [])
                    )
                except EmptyResultSet:
                    if self.elide_empty:
                        raise
                    # Use a predicate that's always False.
                    where, w_params = "0 = 1", []
                having, h_params = (
                    self.compile(self.having) if self.having is not None else ("", [])
                )
                result = []
                params = []
                if where:
                    result.append("WHERE %s" % where)
                    params.extend(w_params)

                grouping = []
                for g_sql, g_params in group_by:
                    grouping.append(g_sql)
                    params.extend(g_params)
                if grouping:
                    if distinct_fields:
                        raise NotImplementedError(
                            "annotate() + distinct(fields) is not implemented."
                        )
                    order_by = order_by or self.connection.ops.force_no_ordering()
                    result.append("GROUP BY %s" % ", ".join(grouping))
                    if self._meta_ordering:
                        order_by = None
                if having:
                    result.append("HAVING %s" % having)
                    params.extend(h_params)

            if self.query.explain_info:
                result.insert(
                    0,
                    self.connection.ops.explain_query_prefix(
                        self.query.explain_info.format,
                        **self.query.explain_info.options,
                    ),
                )

            if order_by:
                ordering = []
                for _, (o_sql, o_params, _) in order_by:
                    ordering.append(o_sql)
                    params.extend(o_params)
                result.append("ORDER BY %s" % ", ".join(ordering))

            if with_limit_offset:
                result.append(
                    self.connection.ops.limit_offset_sql(
                        self.query.low_mark, self.query.high_mark
                    )
                )

            if for_update_part and not features.for_update_after_from:
                result.append(for_update_part)
            from_, f_params = self.get_from_clause()
            sql = " ".join(result)
            if not with_table_name:
                for table_name in from_:
                    sql = sql.replace(table_name + ".", "")
            for key in self.field_replace_dict.keys():
                value = self.field_replace_dict.get(key)
                sql = sql.replace(key, value)
            return sql, tuple(params)
        finally:
            # Finally do cleanup - get rid of the joins we created above.
            self.query.reset_refcounts(refcounts_before)

    def as_sql(self, with_limits=True, with_col_aliases=False, select_string=None):
        if select_string is None:
            return super().as_sql(with_limits, with_col_aliases)
        else:
            sql, params = self.get_query_str(with_table_name=False)
            return (select_string + " " + sql), params
