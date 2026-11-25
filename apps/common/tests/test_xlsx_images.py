from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from openpyxl import Workbook
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
from openpyxl.xml.constants import REL_NS, SHEET_DRAWING_NS
from PIL import Image as PillowImage

from common.handle.impl.common_handle import xlsx_embed_cells_images
from common.handle.impl.text.xlsx_split_handle import XlsxSplitHandle


def picture(color="red"):
    data = BytesIO()
    PillowImage.new("RGB", (8, 6), color).save(data, "PNG")
    return Image(data)


def spreadsheet():
    book = Workbook()
    sheet = book.active
    sheet.title = "Rows"
    sheet.append(["row", "picture"])
    for row in range(2, 9):
        sheet.cell(row, 1, row)
        sheet.add_image(picture(), f"B{row}")
    sheet["B2"] = "caption"
    other = book.create_sheet("Other")
    other["A1"] = "header"
    other["A2"] = "other row"
    anchor = TwoCellAnchor(_from=AnchorMarker(col=2, row=2), to=AnchorMarker(col=3, row=3))
    other.add_image(picture("blue"), anchor)
    other.add_image(picture(), "C3")
    data = BytesIO()
    book.save(data)
    return SimpleUploadedFile("rows.xlsx", data.getvalue())


class XlsxImageTests(SimpleTestCase):
    def test_formula_and_drawing_in_one_cell_share_the_same_saved_image(self):
        book = Workbook()
        book.active["A1"] = "header"
        book.active["A2"] = '=_xlfn.DISPIMG("ID_red",1)'
        book.active.add_image(picture(), "A2")
        book.active["A3"] = '=_xlfn.DISPIMG("ID_red",0)'
        data = BytesIO()
        book.save(data)
        with ZipFile(data, "a") as archive:
            archive.writestr(
                "xl/cellimages.xml",
                f'<cellImages xmlns:xdr="{SHEET_DRAWING_NS}" xmlns:r="{REL_NS}"><xdr:pic>'
                '<xdr:nvPicPr><xdr:cNvPr name="ID_red"/></xdr:nvPicPr>'
                '<xdr:blipFill><blip r:embed="rId1"/></xdr:blipFill></xdr:pic></cellImages>',
            )
            archive.writestr(
                "xl/_rels/cellimages.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="{REL_NS}/image" Target="media/image1.png"/></Relationships>',
            )
        data.seek(0)
        saved = []
        markdown = XlsxSplitHandle().get_content(data, saved.extend)

        self.assertEqual(len(saved), 1)
        link = f"![](./oss/file/{saved[0].id})"
        self.assertIn(f"| {link}<br>{link} |", markdown)
        self.assertNotIn("DISPIMG", markdown)

        formula_files = []
        formulas = xlsx_embed_cells_images(data, formula_files.extend)
        self.assertEqual(len(formula_files), 1)
        self.assertEqual(formulas, {book.active[cell].value: formula_files[0] for cell in ("A2", "A3")})

    def test_repeated_drawings_are_saved_once_and_rendered_in_their_cells(self):
        for method in ("handle", "get_content"):
            with self.subTest(method=method):
                source = spreadsheet()
                saved = []
                parser = XlsxSplitHandle()
                if method == "handle":
                    sheets = parser.handle(source, [], True, 100_000, lambda file: file.read(), saved.extend)
                    markdown = "\n".join(p["content"] for sheet in sheets for p in sheet["content"])
                else:
                    markdown = parser.get_content(source, saved.extend)

                self.assertEqual(len(saved), 2)
                red, blue = [f"![](./oss/file/{file.id})" for file in saved]
                for row in range(2, 9):
                    prefix = "caption<br>" if row == 2 else ""
                    self.assertIn(f"| {row} | {prefix}{red} |", markdown)
                self.assertIn(f"|  |  | {red}<br>{blue} |", markdown)
                self.assertEqual(markdown.count(red), 8)
                for file in saved:
                    with PillowImage.open(BytesIO(file.meta["content"])) as image:
                        image.load()
                        self.assertEqual(image.size, (8, 6))

    @patch("common.handle.impl.common_handle.MAX_EMBED_IMAGE_AGGREGATE_PIXELS", 48)
    def test_reusing_an_image_does_not_consume_the_decode_budget_again(self):
        saved = []
        markdown = XlsxSplitHandle().get_content(spreadsheet(), saved.extend)

        self.assertEqual(len(saved), 1)
        self.assertEqual(markdown.count(f"![](./oss/file/{saved[0].id})"), 8)
