"""Extract and process inline paragraph images without turning them into standalone paragraphs."""

import base64
import json
import mimetypes
import re
from typing import Callable, Dict, Iterable, List, Optional

import uuid_utils.compat as uuid
from common.config.embedding_config import ModelManage
from common.utils.tool_code import ToolExecutor
from django.db import transaction
from langchain_core.messages import HumanMessage
from models_provider.models import Model
from models_provider.tools import get_model
from tools.models import Tool

from knowledge.models import AssetProcessStatus, Embedding, File, Paragraph, ParagraphAsset, SourceType, SyncState
from knowledge.services.document_strategy import normalize_document_strategy, strategy_hashes


IMAGE_PATTERN = re.compile(r"!\[(?P<caption>[^\]]*)\]\([^)]*/oss/file/(?P<file_id>[0-9a-fA-F-]{32,36})[^)]*\)")


def paragraph_content_schema(content: str) -> List[Dict]:
    blocks, cursor = [], 0
    for match in IMAGE_PATTERN.finditer(content or ""):
        if match.start() > cursor:
            blocks.append({"type": "text", "content": content[cursor : match.start()]})
        blocks.append(
            {
                "type": "image",
                "file_id": match.group("file_id"),
                "caption": match.group("caption") or "",
                "description": "",
                "raw": match.group(0),
            }
        )
        cursor = match.end()
    if cursor < len(content or ""):
        blocks.append({"type": "text", "content": content[cursor:]})
    return blocks or [{"type": "text", "content": content or ""}]


@transaction.atomic
def sync_paragraph_assets(paragraphs: Iterable[Paragraph], visual_strategy_hash: str = "") -> List[ParagraphAsset]:
    active_assets = []
    for paragraph in paragraphs:
        schema = paragraph_content_schema(paragraph.content)
        expected = set()
        image_position = 0
        for block in schema:
            if block["type"] != "image":
                continue
            image_position += 1
            file = File.objects.filter(id=block["file_id"]).first()
            if file is None:
                continue
            source_key = f"{paragraph.source_key or paragraph.id}:image:{image_position}:{file.sha256_hash or file.id}"
            expected.add(source_key)
            asset, _ = ParagraphAsset.objects.update_or_create(
                document_id=paragraph.document_id,
                source_asset_key=source_key,
                defaults={
                    "knowledge_id": paragraph.knowledge_id,
                    "paragraph_id": paragraph.id,
                    "file_id": file.id,
                    "position": image_position,
                    "source_hash": file.sha256_hash,
                    "caption": block["caption"],
                    "sync_state": SyncState.ACTIVE,
                    "visual_strategy_hash": visual_strategy_hash,
                },
            )
            block["caption"] = asset.caption
            block["ocr_text"] = asset.ocr_text
            block["description"] = asset.description
            active_assets.append(asset)
        paragraph.content_schema = schema
        paragraph.save(update_fields=["content_schema", "update_time"])
        ParagraphAsset.objects.filter(paragraph=paragraph).exclude(source_asset_key__in=expected).update(
            sync_state=SyncState.REMOTE_DELETED
        )
    return active_assets


def process_visual_assets(
    assets: Iterable[ParagraphAsset],
    strategy: Dict | None,
    processor: Optional[Callable[[ParagraphAsset, Dict], Dict]] = None,
) -> None:
    """Run a model/tool adapter. Errors are isolated per image and never abort document import."""
    normalized = normalize_document_strategy(strategy)
    visual = normalized["visual"]
    visual_hash = strategy_hashes(normalized)["visual_strategy_hash"]
    resolver_error = ""
    if visual["enabled"] and processor is None:
        try:
            processor = resolve_visual_processor(visual)
        except Exception as exc:
            resolver_error = str(exc)[:2000]
    for asset in assets:
        asset.visual_strategy_hash = visual_hash
        if not visual["enabled"]:
            asset.process_status = AssetProcessStatus.SKIPPED
            asset.process_error = ""
        elif processor is None:
            asset.process_status = AssetProcessStatus.FAILURE
            asset.process_error = resolver_error or "visual processor adapter is unavailable"
        else:
            try:
                output = processor(asset, visual) or {}
                asset.caption = output.get("caption", asset.caption)
                asset.ocr_text = output.get("ocr_text", "")
                asset.description = output.get("description", "")
                asset.meta = {**asset.meta, **(output.get("meta") or {})}
                asset.process_status = AssetProcessStatus.SUCCESS
                asset.process_error = ""
            except Exception as exc:  # Image failure must not interrupt the remaining document.
                asset.process_status = AssetProcessStatus.FAILURE
                asset.process_error = str(exc)[:2000]
        asset.save(
            update_fields=[
                "caption",
                "ocr_text",
                "description",
                "meta",
                "process_status",
                "process_error",
                "visual_strategy_hash",
                "update_time",
            ]
        )
        _write_asset_description(asset)


def _write_asset_description(asset: ParagraphAsset) -> None:
    paragraph = Paragraph.objects.filter(id=asset.paragraph_id).first()
    if paragraph is None:
        return
    schema = paragraph.content_schema or paragraph_content_schema(paragraph.content)
    images = [block for block in schema if block.get("type") == "image"]
    index = asset.position - 1
    if index < 0 or index >= len(images):
        return
    images[index]["caption"] = asset.caption
    images[index]["ocr_text"] = asset.ocr_text
    images[index]["description"] = asset.description
    paragraph.content_schema = schema
    paragraph.save(update_fields=["content_schema", "update_time"])


def _image_data_url(asset: ParagraphAsset) -> str:
    mime = mimetypes.guess_type(asset.file.file_name)[0] or "application/octet-stream"
    encoded = base64.b64encode(asset.file.get_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _get_llm_model(model_id):
    model = Model.objects.filter(id=model_id).first()
    return ModelManage.get_model(model_id, lambda _id: get_model(model))


def resolve_visual_processor(visual: Dict) -> Optional[Callable[[ParagraphAsset, Dict], Dict]]:
    if visual.get("strategy") == "model":
        model = _get_llm_model(visual["model_id"])

        def model_processor(asset: ParagraphAsset, _config: Dict) -> Dict:
            prompt = (
                "请识别图片中的文字并描述图片。只返回 JSON："
                '{"description":"图片描述","ocr_text":"识别文字","caption":"简短标题"}'
            )
            response = model.invoke(
                [
                    HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": _image_data_url(asset)}},
                        ]
                    )
                ]
            )
            content = response.content if hasattr(response, "content") else response
            if isinstance(content, list):
                content = "".join(
                    str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in content
                )
            text = str(content).strip().removeprefix("```json").removesuffix("```").strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"description": text}

        return model_processor

    if visual.get("strategy") == "tool":
        tool = Tool.objects.filter(id=visual["tool_id"], is_active=True).first()
        if tool is None:
            return None

        def tool_processor(asset: ParagraphAsset, _config: Dict) -> Dict:
            data_url = _image_data_url(asset)
            available = {
                "file_id": str(asset.file_id),
                "image": data_url,
                "image_url": data_url,
                "image_base64": data_url.split(",", 1)[1],
            }
            params = {
                field.get("name"): available.get(field.get("name"))
                for field in (tool.input_field_list or [])
                if field.get("name") in available
            }
            init_params = tool.init_params
            if isinstance(init_params, str) and init_params.strip():
                init_params = json.loads(init_params)
            output = ToolExecutor().exec_code(tool.code, {**(init_params or {}), **params})
            if isinstance(output, dict):
                return output
            return {"description": str(output)}

        return tool_processor
    return None


def embed_paragraph_assets(paragraph_ids: Iterable[str], embedding_model) -> int:
    """Create image vectors only when the selected embedding model declares image capability."""
    if not embedding_model.supports_image_embedding():
        return 0
    assets = list(
        ParagraphAsset.objects.select_related("file", "paragraph")
        .filter(paragraph_id__in=paragraph_ids, sync_state=SyncState.ACTIVE)
        .order_by("paragraph_id", "position")
    )
    if not assets:
        return 0
    image_inputs = []
    for asset in assets:
        image_inputs.append(_image_data_url(asset))
    vectors = embedding_model.embed_images(image_inputs)
    rows = []
    for asset, vector in zip(assets, vectors):
        rows.append(
            Embedding(
                id=uuid.uuid7(),
                knowledge_id=asset.knowledge_id,
                document_id=asset.document_id,
                paragraph_id=asset.paragraph_id,
                source_id=str(asset.id),
                source_type=SourceType.IMAGE,
                is_active=asset.paragraph.is_active,
                embedding=[float(item) for item in vector],
                search_vector="",
                meta={"unit_type": "image", "asset_id": str(asset.id), "position": asset.position},
            )
        )
    Embedding.objects.bulk_create(rows)
    return len(rows)
