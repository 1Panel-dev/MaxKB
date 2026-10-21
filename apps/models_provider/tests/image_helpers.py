"""Synthetic image fixtures shared by embedding tests."""

import base64
from io import BytesIO

from PIL import Image


def image_data_url(size, mode="RGB", color="black", image_format="PNG"):
    output = BytesIO()
    Image.new(mode, size, color).save(output, format=image_format)
    mime = "image/jpeg" if image_format == "JPEG" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(output.getvalue()).decode("ascii")


def decode_image(data_url):
    return Image.open(BytesIO(base64.b64decode(data_url.split(";base64,", 1)[1])))


def svg_data_url(content='<rect width="100%" height="100%" fill="red"/>', size=(88, 20), attributes=None):
    if attributes is None:
        attributes = f'width="{size[0]}" height="{size[1]}"'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" {attributes}>{content}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode("ascii")
