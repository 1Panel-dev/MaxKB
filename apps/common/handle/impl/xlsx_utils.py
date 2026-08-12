# coding=utf-8


def get_sheet_content_max_column(sheet):
    return max(
        (cell.column for cell in sheet._cells.values() if cell.value is not None),
        default=0,
    )


def iter_sheet_content_rows(sheet, min_row=1):
    max_column = get_sheet_content_max_column(sheet)
    if max_column == 0:
        return iter(())
    return sheet.iter_rows(min_row=min_row, max_col=max_column)
