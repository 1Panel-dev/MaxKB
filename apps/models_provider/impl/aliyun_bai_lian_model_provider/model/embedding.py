# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/16 16:34
@desc:
"""

import base64
import math
import re
from http import HTTPStatus
from io import BytesIO
from typing import Dict, List
from urllib.parse import unquote_to_bytes
from xml.etree import ElementTree

import dashscope
import resvg_py
from openai import OpenAI
from PIL import Image, ImageOps

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class AliyunBaiLianEmbedding(MaxKBBaseEmbeddingModel):
    model_name: str
    optional_params: dict
    api_base: str
    api_key: str

    def __init__(self, api_key, model_name: str, api_base: str, optional_params: dict):
        self.client = OpenAI(api_key=api_key, base_url=api_base).embeddings
        self.model_name = model_name
        self.optional_params = optional_params
        self.api_key = api_key
        self.api_base = api_base

    def is_cache_model(self):
        return False

    @staticmethod
    def _is_multimodal(model_name: str) -> bool:
        """判断模型是否为多模态向量模型（支持图片/视频独立向量）。"""
        model_name = model_name.lower()
        return any(k in model_name for k in ("vl-embedding", "embedding-vision", "multimodal"))

    def supports_image_embedding(self) -> bool:
        return self._is_multimodal(self.model_name)

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseEmbeddingModel.filter_optional_params(model_kwargs)
        return AliyunBaiLianEmbedding(
            api_key=model_credential.get("dashscope_api_key"),
            model_name=model_name,
            api_base=model_credential.get("api_base") or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            optional_params=optional_params,
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(self, texts: List[str], chunk_size: int | None = None) -> List[List[float]]:
        # 处理多模态的向量化
        if self._is_multimodal(self.model_name):
            return self._call_multimodal([{"text": text} for text in texts])

        if len(self.optional_params) > 0:
            res = self.client.create(
                input=texts, model=self.model_name, encoding_format="float", **self.optional_params
            )
        else:
            res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]

    def embed_images(self, images: List[str]) -> List[List[float]]:
        """对图片 URL / data URL 做独立向量化（每张图生成一个向量）。"""
        if not self.supports_image_embedding():
            return []
        return self._call_multimodal([{"image": self._prepare_image_input(image)} for image in images])

    def _prepare_image_input(self, image: str) -> str:
        image = self.normalize_image_input(image, keep_data_prefix=True)
        if (
            "qwen3-vl-embedding" not in self.model_name.lower()
            or not image.startswith("data:image/")
            or ";base64," not in image
        ):
            return image

        image_bytes = base64.b64decode(image.split(";base64,", 1)[1], validate=True)
        if image.split(";", 1)[0].lower() == "data:image/svg+xml":
            # Pillow cannot decode SVG. Render only the request copy, including embedded
            # SVG logos, and keep raster dimensions bounded while preserving the aspect ratio.
            svg = self._sanitize_svg(image_bytes)
            image_bytes = self._render_svg(svg)
            image = "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")

        with Image.open(BytesIO(image_bytes)) as source:
            # Qwen3 rounds resized sides to multiples of 32 and rejects aspect ratios above 200.
            # Imported documents can contain 1-2 pixel separator images; pad the request copy
            # so one such image cannot invalidate the entire paragraph's embedding batch.
            minimum_side = max(32, math.ceil(max(source.size) / 200))
            if min(source.size) >= minimum_side:
                return image
            source = ImageOps.exif_transpose(source).convert("RGBA")
            width, height = source.size
            padded = Image.new("RGB", (max(width, minimum_side), max(height, minimum_side)), "white")
            padded.paste(source, ((padded.width - width) // 2, (padded.height - height) // 2), source)
            output = BytesIO()
            padded.save(output, format="PNG")
        return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")

    @staticmethod
    def _render_svg(svg: str) -> bytes:
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
        scale = min(1.0, 2048 / max(width, height))
        # Fix the original viewport in pixels, independently of the output dimensions.
        # Otherwise percentage dimensions could resolve against the smaller output size.
        root.set("width", str(width))
        root.set("height", str(height))
        return resvg_py.svg_to_bytes(
            svg_string=ElementTree.tostring(root, encoding="unicode"),
            width=max(1, math.floor(width * scale + 0.5)),
            height=max(1, math.floor(height * scale + 0.5)),
            dpi=96,
            background="white",
        )

    @staticmethod
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
                        sanitized = AliyunBaiLianEmbedding._sanitize_svg(embedded, depth + 1).encode("utf-8")
                        node.attrib[key] = "data:image/svg+xml;base64," + base64.b64encode(sanitized).decode("ascii")
                    else:
                        # Reject SVG disguised as a raster data URL before handing it to resvg.
                        with Image.open(BytesIO(embedded)) as raster:
                            raster.verify()
        return ElementTree.tostring(root, encoding="unicode")

    def _multimodal_base_url(self) -> str:
        """DashScope 原生多模态接口走 /api/v1，与 OpenAI 兼容地址区分开。"""
        base = self.api_base or "https://dashscope.aliyuncs.com/api/v1"
        if "/compatible-mode/" in base:
            return base.split("/compatible-mode/")[0] + "/api/v1"
        return base

    def _call_multimodal(self, items: List[dict]) -> List[List[float]]:
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = self._multimodal_base_url()
        resp = dashscope.MultiModalEmbedding.call(
            model=self.model_name,
            input=items,  # type: ignore
            **self.optional_params,
        )

        if resp.status_code == HTTPStatus.OK:
            embeddings_data = resp.output.get("embeddings", [])
            return [item.get("embedding", []) for item in embeddings_data]
        raise Exception(f"MultiModalEmbedding call failed: status={resp.status_code}, message={resp.message}")
