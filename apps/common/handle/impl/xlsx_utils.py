# coding=utf-8
from common.handle.impl.common_handle import read_xlsx_images
from common.utils.logger import maxkb_logger


def get_sheet_content_max_column(sheet):
    return max(
        (cell.column for cell in sheet._cells.values() if cell.value is not None),
        default=0,
    )


def iter_sheet_content_rows(sheet, min_row=1, *, drawings=None):
    width = get_sheet_content_max_column(sheet)
    if drawings:
        width = max(width, max(column for row, column in drawings))
    if not width:
        return
    last_row = sheet.max_row
    yield from sheet.iter_rows(min_row=min_row, max_row=last_row, max_col=width)
    # Images can extend past the last data row; visit just those additional rows.
    if drawings:
        for row in sorted({row for row, column in drawings if row > last_row and row >= min_row}):
            yield from sheet.iter_rows(min_row=row, max_row=row, max_col=width)


def load_images(source, workbook, save_image):
    if save_image is None:
        return {}, {}
    try:
        return read_xlsx_images(source, workbook, save_image)
    except Exception:
        maxkb_logger.exception("Error processing embedded XLSX images")
        return {}, {}


def cell_content(value, formula_images, drawings):
    formula_image = formula_images.get(value)
    if formula_image is not None:
        value = f"![](./oss/file/{formula_image.id})"
    if drawings:
        parts = [str(value)] if value is not None and value != "" else []
        parts.extend(f"![](./oss/file/{image.id})" for image in drawings)
        return "\n".join(parts)
    return value


def merged_row_values(sheet, row, image_dict, drawings):
    for cell in row:
        value = cell.value
        if value is None:
            for merged_range in sheet.merged_cells.ranges:
                if cell.coordinate in merged_range:
                    value = sheet.cell(merged_range.min_row, merged_range.min_col).value
                    break
        yield cell_content(value, image_dict, drawings.get((cell.row, cell.column)))
