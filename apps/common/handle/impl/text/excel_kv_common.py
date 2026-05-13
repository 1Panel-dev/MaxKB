# coding=utf-8
"""
    @project: maxkb
    @file: excel_kv_common.py
    @desc: Excel / CSV 知识化共享逻辑。

    把每一行结构化数据序列化为"文件 + 工作表 + 行号 + 表头:值"形式的 paragraph，
    比裸 markdown 表格更友好于向量检索。
    被 xlsx_split_handle / xls_split_handle / csv_split_handle 复用。
"""
import datetime
from typing import List, Optional


# 单 chunk 字符上限（safeguard），超过会回退到强制截断
_HARD_LIMIT_FALLBACK = 100000


def normalize_value(val, image_dict: Optional[dict] = None) -> str:
    """把单元格值规范化成字符串。

    - None → ''
    - datetime/date → ISO 字符串（去掉 00:00:00 尾巴）
    - float 表示整数 → 显示为整数（避免 12000 显示成 12000.0）
    - 含换行符的字符串 → 保留换行（kv 块本来就是多行格式，比 markdown 表格少负担）
    - 命中 image_dict 的值 → 替换为 markdown 图片链接
    """
    if val is None:
        return ''

    # 图片优先：用原始值（未转字符串）做 key 查找，与现有 xlsx_split_handle.post_cell 一致
    if image_dict:
        image = image_dict.get(val, None)
        if image is not None:
            return f'![](./oss/file/{image.id})'

    # datetime / date
    if isinstance(val, datetime.datetime):
        if val.hour == 0 and val.minute == 0 and val.second == 0 and val.microsecond == 0:
            return val.strftime('%Y-%m-%d')
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, datetime.date):
        return val.strftime('%Y-%m-%d')

    # float 表示整数（openpyxl 把整数读成 float 的情况）
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val)

    text = str(val).strip()
    # 已知保留情况：含换行的多行单元格保留换行，kv 块本来就允许多行
    return text


def _has_any_value(values: List) -> bool:
    """整行是否至少有一个非空单元格。"""
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == '':
            continue
        return True
    return False


def make_kv_paragraph(
        file_name: str,
        sheet_name: Optional[str],
        row_idx: int,
        headers: List[str],
        row_values: List,
        image_dict: Optional[dict] = None,
        limit: int = _HARD_LIMIT_FALLBACK,
) -> Optional[dict]:
    """单行 → 一个 paragraph dict（{'title', 'content'}）。

    Returns:
      - None：整行全空，应被跳过
      - dict：可以加入 paragraphs 列表
    """
    if not _has_any_value(row_values):
        return None

    lines = [f'文件：{file_name}']
    if sheet_name:
        lines.append(f'工作表：{sheet_name}')
    lines.append(f'行号：第 {row_idx} 行')
    lines.append('---')

    for idx, raw_value in enumerate(row_values):
        # 标题对齐（行比表头长时用 col_N 占位）
        if idx < len(headers):
            header = headers[idx]
        else:
            header = f'col{idx + 1}'
        if header is None:
            header = f'col{idx + 1}'
        header = str(header).strip()
        if not header:
            header = f'col{idx + 1}'

        value_text = normalize_value(raw_value, image_dict)
        if value_text == '':
            # 跳过空值，避免「客户名称：」这种噪声
            continue
        lines.append(f'{header}：{value_text}')

    content = '\n'.join(lines)

    # 安全网：超长 chunk 截断（极少触发，单元格里塞了大段文本时才会）
    if len(content) > limit:
        content = content[:limit]

    if sheet_name:
        title = f'{file_name} / {sheet_name} / 第{row_idx}行'
    else:
        title = f'{file_name} / 第{row_idx}行'

    return {'title': title, 'content': content}


def normalize_headers(raw_headers: List) -> List[str]:
    """规范化表头：None / 空 → col1/col2/..."""
    headers = []
    for idx, h in enumerate(raw_headers):
        if h is None:
            headers.append(f'col{idx + 1}')
            continue
        text = str(h).strip()
        if not text:
            headers.append(f'col{idx + 1}')
        else:
            headers.append(text)
    return headers
