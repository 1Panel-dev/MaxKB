"""Prepare inline images for embedding without changing stored source files."""

import base64
import math
import re
from io import BytesIO
from urllib.parse import unquote_to_bytes
from xml.etree import ElementTree

import resvg_py
from PIL import Image, ImageOps


def prepare_embedding_image(
    image: str,
    *,
    min_side: int = 1,
    max_aspect_ratio: float | None = None,
    min_pixels: int = 1,
    max_svg_side: int = 2048,
    max_svg_pixels: int | None = None,
) -> str:
    """Render SVG at its intrinsic size (capped before rendering), then pad to model limits.

    Keep HTTP URLs and opaque provider inputs unchanged. Raster images are only
    decoded when a model needs dimension checks; valid images keep their encoding.
    """
    if not image.startswith("data:image/") or "," not in image:
        return image
    header, content = image.split(",", 1)
    is_svg = header.split(";", 1)[0].lower() == "data:image/svg+xml"
    needs_padding_check = min_side > 1 or max_aspect_ratio is not None or min_pixels > 1
    if not is_svg and not needs_padding_check:
        return image
    image_bytes = base64.b64decode(content, validate=True) if header.endswith(";base64") else unquote_to_bytes(content)
    if is_svg:
        image_bytes = _render_svg(_sanitize_svg(image_bytes), max_svg_side, max_svg_pixels)
        image = "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")
    if not needs_padding_check:
        return image

    with Image.open(BytesIO(image_bytes)) as source:
        minimum_side = min_side
        if max_aspect_ratio is not None:
            minimum_side = max(minimum_side, math.ceil(max(source.size) / max_aspect_ratio))
        width, height = max(source.width, minimum_side), max(source.height, minimum_side)
        if width * height < min_pixels:
            # Grow the canvas, never the content. Balance tiny images while only
            # adding to the shorter side when the longer side is already sufficient.
            side = math.ceil(math.sqrt(min_pixels))
            if width >= height:
                width = max(width, side)
                height = max(height, math.ceil(min_pixels / width))
            else:
                height = max(height, side)
                width = max(width, math.ceil(min_pixels / height))
        if (width, height) == source.size:
            return image
        original_size = source.size
        source = ImageOps.exif_transpose(source).convert("RGBA")
        # EXIF rotation can swap the axes; keep the padding aligned with the image.
        if source.size != original_size:
            width, height = height, width
        padded = Image.new("RGB", (width, height), "white")
        padded.paste(source, ((width - source.width) // 2, (height - source.height) // 2), source)
        output = BytesIO()
        padded.save(output, format="PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def _render_svg(svg: str, max_side: int, max_pixels: int | None) -> bytes:
    """Resolve the viewport before rendering so large SVGs never allocate a full-size bitmap."""
    root = ElementTree.fromstring(svg)
    # SVGs without intrinsic dimensions use a 300 x 150 viewport. A viewBox supplies
    # the reference dimensions for omitted or percentage width/height instead.
    reference_width, reference_height = 300.0, 150.0
    if root.get("viewBox"):
        view_box = [float(value) for value in re.split(r"[\s,]+", root.get("viewBox").strip())]
        if len(view_box) != 4 or not all(math.isfinite(value) for value in view_box) or min(view_box[2:]) <= 0:
            raise ValueError("Invalid SVG viewBox")
        reference_width, reference_height = view_box[2:]

    def dimension(name: str, reference: float) -> float:
        value = root.get(name, "100%").strip()
        match = re.fullmatch(r"([+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-z%]*)", value)
        units = {
            "": 1,
            "px": 1,
            "in": 96,
            "cm": 96 / 2.54,
            "mm": 96 / 25.4,
            "pt": 96 / 72,
            "pc": 16,
            "%": reference / 100,
        }
        if match is None or match[2] not in units:
            raise ValueError(f"Unsupported SVG {name}")
        pixels = float(match[1]) * units[match[2]]
        if not math.isfinite(pixels) or pixels <= 0:
            raise ValueError(f"Invalid SVG {name}")
        return pixels

    width, height = dimension("width", reference_width), dimension("height", reference_height)
    scale = min(1.0, max_side / max(width, height))
    if max_pixels is not None:
        scale = min(scale, math.sqrt(max_pixels / width / height))
    output_width, output_height = max(1, math.floor(width * scale + 0.5)), max(1, math.floor(height * scale + 0.5))
    if max_pixels is not None and output_width * output_height > max_pixels:
        if output_width >= output_height:
            output_width = max(1, max_pixels // output_height)
        else:
            output_height = max(1, max_pixels // output_width)
    # Fix the original viewport in pixels, independently of the output dimensions.
    # Otherwise percentage dimensions could resolve against the smaller output size.
    root.set("width", str(width))
    root.set("height", str(height))
    return resvg_py.svg_to_bytes(
        svg_string=ElementTree.tostring(root, encoding="unicode"),
        width=output_width,
        height=output_height,
        dpi=96,
        background="white",
    )


def _sanitize_svg(data: bytes, depth: int = 0) -> str:
    """Keep SVG rendering self-contained; never let document images read server files."""
    if depth > 4:
        raise ValueError("SVG image nesting exceeds the supported depth")
    root = ElementTree.fromstring(data)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Expected an SVG image")
    for node in root.iter():
        for key, value in list(node.attrib.items()):
            if key.rsplit("}", 1)[-1] != "href":
                continue
            value = value.strip()
            if node.tag == "{http://www.w3.org/2000/svg}a":
                del node.attrib[key]  # Links have no effect on the rendered image.
            elif value and not value.startswith("#"):
                if not value.startswith("data:image/") or "," not in value:
                    raise ValueError("SVG images with external resources are not supported")
                header, content = value.split(",", 1)
                embedded = (
                    base64.b64decode(content, validate=True)
                    if header.endswith(";base64")
                    else unquote_to_bytes(content)
                )
                if header.split(";", 1)[0] == "data:image/svg+xml":
                    sanitized = _sanitize_svg(embedded, depth + 1).encode("utf-8")
                    node.attrib[key] = "data:image/svg+xml;base64," + base64.b64encode(sanitized).decode("ascii")
                else:
                    # Reject SVG disguised as a raster data URL before handing it to resvg.
                    with Image.open(BytesIO(embedded)) as raster:
                        raster.verify()
    return ElementTree.tostring(root, encoding="unicode")
