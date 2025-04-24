# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： compiler.py
    @date：2023/10/7 10:53
    @desc:
"""

from django.core.exceptions import EmptyResultSet, FullResultSet
from django.db import NotSupportedError
from django.db.models.sql.compiler import SQLCompiler
from django.db.transaction import TransactionManagementError


class AppSQLCompiler(SQLCompiler):
    def __init__(self, query, connection, using, elide_empty=True, field_replace_dict=None):
        super().__init__(query, connection, using, elide_empty)
        if field_replace_dict is None:
            field_replace_dict = {}
        self.field_replace_dict = field_replace_dict

    def get_query_str(self, with_limits=True, with_table_name=False, with_col_aliases=False):
        refcounts_before = self.query.alias_refcount.copy()
        try:
            combinator = self.query.combinator
            extra_select, order_by, group_by = self.pre_sql_setup(
                with_col_aliases=with_col_aliases or bool(combinator),
            )
            for_update_part = None
            # Is a LIMIT/OFFSET clause needed?
            with_limit_offset = with_limits and self.query.is_sliced
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
            elif self.qualify:
                result, params = self.get_qualify_sql()
                order_by = None
            else:
                distinct_fields, distinct_params = self.get_distinct()
                # This must come after 'select', 'ordering', and 'distinct'
                # (see docstring of get_from_clause() for details).
                from_, f_params = self.get_from_clause()
                try:
                    where, w_params = (
                        self.compile(self.where) if self.where is not None else ("", [])
                    )
                except EmptyResultSet:
                    if self.elide_empty:
                        raise
                    # Use a predicate that's always False.
                    where, w_params = "0 = 1", []
                except FullResultSet:
                    where, w_params = "", []
                try:
                    having, h_params = (
                        self.compile(self.having)
                        if self.having is not None
                        else ("", [])
                    )
                except FullResultSet:
                    having, h_params = "", []
                result = []
                params = []

                if self.query.distinct:
                    distinct_result, distinct_params = self.connection.ops.distinct_sql(
                        distinct_fields,
                        distinct_params,
                    )
                    result += distinct_result
                    params += distinct_params

                out_cols = []
                for _, (s_sql, s_params), alias in self.select + extra_select:
                    if alias:
                        s_sql = "%s AS %s" % (
                            s_sql,
                            self.connection.ops.quote_name(alias),
                        )
                    params.extend(s_params)
                    out_cols.append(s_sql)

                params.extend(f_params)

                if self.query.select_for_update and features.has_select_for_update:
                    if (
                            self.connection.get_autocommit()
                            # Don't raise an exception when database doesn't
                            # support transactions, as it's a noop.
                            and features.supports_transactions
                    ):
                        raise TransactionManagementError(
                            "select_for_update cannot be used outside of a transaction."
                        )

                    if (
                            with_limit_offset
                            and not features.supports_select_for_update_with_limit
                    ):
                        raise NotSupportedError(
                            "LIMIT/OFFSET is not supported with "
                            "select_for_update on this database backend."
                        )
                    nowait = self.query.select_for_update_nowait
                    skip_locked = self.query.select_for_update_skip_locked
                    of = self.query.select_for_update_of
                    no_key = self.query.select_for_no_key_update
                    # If it's a NOWAIT/SKIP LOCKED/OF/NO KEY query but the
                    # backend doesn't support it, raise NotSupportedError to
                    # prevent a possible deadlock.
                    if nowait and not features.has_select_for_update_nowait:
                        raise NotSupportedError(
                            "NOWAIT is not supported on this database backend."
                        )
                    elif skip_locked and not features.has_select_for_update_skip_locked:
                        raise NotSupportedError(
                            "SKIP LOCKED is not supported on this database backend."
                        )
                    elif of and not features.has_select_for_update_of:
                        raise NotSupportedError(
                            "FOR UPDATE OF is not supported on this database backend."
                        )
                    elif no_key and not features.has_select_for_no_key_update:
                        raise NotSupportedError(
                            "FOR NO KEY UPDATE is not supported on this "
                            "database backend."
                        )
                    for_update_part = self.connection.ops.for_update_sql(
                        nowait=nowait,
                        skip_locked=skip_locked,
                        of=self.get_select_for_update_of_arguments(),
                        no_key=no_key,
                    )

                if for_update_part and features.for_update_after_from:
                    result.append(for_update_part)

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
                order_by_sql = "ORDER BY %s" % ", ".join(ordering)
                if combinator and features.requires_compound_order_by_subquery:
                    result = ["SELECT * FROM (", *result, ")", order_by_sql]
                else:
                    result.append(order_by_sql)

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
