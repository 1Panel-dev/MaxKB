"""Synthetic PDFs for parser regression tests, without additional fixture dependencies."""

import io

from pypdf import PdfWriter
from pypdf.annotations import Link
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    Fit,
    NameObject,
    NumberObject,
    TextStringObject,
)


def content_pdf(pages, *, bookmarks=(), links=(), image=False, password=None):
    """Each page contains (text, y, font_size) lines; bookmarks contain (title, page, top)."""
    writer = PdfWriter()
    characters = sorted({char for lines in pages for text, _y, _size in lines for char in text})
    mappings = "\n".join(
        f"<{char.encode('utf-16-be').hex()}> <{char.encode('utf-16-be').hex()}>" for char in characters
    )
    cmap = DecodedStreamObject()
    cmap.set_data(
        (
            "/CIDInit /ProcSet findresource begin 12 dict begin begincmap\n"
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
            "/CMapName /FixtureUnicode def /CMapType 2 def\n"
            "1 begincodespacerange <0000> <FFFF> endcodespacerange\n"
            f"{len(characters)} beginbfchar\n{mappings}\nendbfchar\n"
            "endcmap CMapName currentdict /CMap defineresource pop end end"
        ).encode("ascii")
    )
    descendant = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/CIDFontType0"),
            NameObject("/BaseFont"): NameObject("/STSong-Light"),
            NameObject("/CIDSystemInfo"): DictionaryObject(
                {
                    NameObject("/Registry"): TextStringObject("Adobe"),
                    NameObject("/Ordering"): TextStringObject("GB1"),
                    NameObject("/Supplement"): NumberObject(0),
                }
            ),
            NameObject("/DW"): NumberObject(1000),
        }
    )
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type0"),
                NameObject("/BaseFont"): NameObject("/STSong-Light"),
                NameObject("/Encoding"): NameObject("/Identity-H"),
                NameObject("/DescendantFonts"): ArrayObject([writer._add_object(descendant)]),
                NameObject("/ToUnicode"): writer._add_object(cmap),
            }
        )
    )
    for index, lines in enumerate(pages):
        page = writer.add_blank_page(width=612, height=792)
        resources = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
        page[NameObject("/Resources")] = resources
        commands = [
            f"BT /F1 {size} Tf 1 0 0 1 72 {y} Tm <{text.encode('utf-16-be').hex()}> Tj ET" for text, y, size in lines
        ]
        if image and index == 0:
            bitmap = DecodedStreamObject()
            bitmap.update(
                {
                    NameObject("/Type"): NameObject("/XObject"),
                    NameObject("/Subtype"): NameObject("/Image"),
                    NameObject("/Width"): NumberObject(2),
                    NameObject("/Height"): NumberObject(2),
                    NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
                    NameObject("/BitsPerComponent"): NumberObject(8),
                }
            )
            bitmap.set_data(bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255]))
            resources[NameObject("/XObject")] = DictionaryObject({NameObject("/Im1"): writer._add_object(bitmap)})
            commands.append("q 40 0 0 40 72 100 cm /Im1 Do Q")
        stream = DecodedStreamObject()
        stream.set_data("\n".join(commands).encode("ascii"))
        page[NameObject("/Contents")] = writer._add_object(stream)
        page.compress_content_streams()
    for title, page_number, top in bookmarks:
        writer.add_outline_item(title, page_number, fit=Fit.xyz(left=0, top=top, zoom=0))
    for source, target, rect in links:
        writer.add_annotation(source, Link(rect=rect, target_page_index=target))
    if password is not None:
        writer.encrypt(password, owner_password="fixture-owner", algorithm="AES-256")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()
