"""Extract and process inline paragraph images without turning them into standalone paragraphs."""

import base64
import json
import mimetypes
import re
from typing import Callable, Dict, Iterable, List, Optional

import uuid_utils.compat as uuid
from common.config.embedding_config import ModelManage
from common.exception.app_exception import AppApiException
from common.utils.shared_resource_auth import filter_authorized_ids
from common.utils.tool_code import ToolExecutor
from common.utils.ts_vecto_util import to_ts_vector
from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.db.models import Value
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage
from models_provider.base_model_provider import ModelTypeConst
from models_provider.tools import get_model, get_model_by_id
from tools.models import Tool

from knowledge.models import (
    AssetProcessStatus,
    ContentOrigin,
    Embedding,
    File,
    Paragraph,
    ParagraphAsset,
    SourceType,
    SyncState,
)
from knowledge.services.document_strategy import normalize_document_strategy, strategy_hashes


IMAGE_PATTERN = re.compile(r"!\[(?P<caption>[^\]]*)\]\([^)]*/oss/file/(?P<file_id>[0-9a-fA-F-]{32,36})[^)]*\)")


def paragraph_asset_source_key(paragraph: Paragraph, position: int) -> str:
    return f"{paragraph.source_key or paragraph.id}:image:{position}"


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
    paragraphs = list(paragraphs)
    if not paragraphs:
        return []

    document_ids = {paragraph.document_id for paragraph in paragraphs}
    touched_paragraph_ids = {paragraph.id for paragraph in paragraphs}
    existing_assets = list(
        ParagraphAsset.objects.select_for_update()
        .select_related("paragraph")
        .filter(document_id__in=document_ids)
        .order_by("document_id", "paragraph_id", "position", "id")
    )
    existing_keys = {(asset.document_id, asset.source_asset_key) for asset in existing_assets if asset.source_asset_key}
    claimed_ids = set()
    plans = []
    schemas = {}

    def available_assets(paragraph, origin):
        return [
            asset
            for asset in existing_assets
            if asset.document_id == paragraph.document_id
            and asset.origin == origin
            and asset.id not in claimed_ids
            and (
                asset.paragraph_id == paragraph.id
                or (
                    origin == ContentOrigin.SYNCED
                    and (
                        asset.paragraph_id in touched_paragraph_ids
                        or not asset.paragraph.is_active
                        or asset.paragraph.sync_state == SyncState.REMOTE_DELETED
                    )
                )
            )
        ]

    def unique_source_key(paragraph, desired_key, file_hash):
        candidate = desired_key[:512]
        index = 1
        while (paragraph.document_id, candidate) in existing_keys:
            suffix = f":{(file_hash or 'asset')[:12]}:{index}"
            candidate = f"{desired_key[: 512 - len(suffix)]}{suffix}"
            index += 1
        existing_keys.add((paragraph.document_id, candidate))
        return candidate

    # Match every image before applying remote-delete markers. This allows an image to move
    # between changed paragraphs while retaining its ParagraphAsset id and recall history.
    for paragraph in paragraphs:
        schema = paragraph_content_schema(paragraph.content)
        schemas[paragraph.id] = schema
        image_position = 0
        for block in schema:
            if block["type"] != "image":
                continue
            image_position += 1
            file = File.objects.filter(id=block["file_id"]).first()
            if file is None:
                continue
            origin = ContentOrigin.SYNCED if paragraph.origin == ContentOrigin.SYNCED else ContentOrigin.MANUAL
            candidates = available_assets(paragraph, origin)
            desired_key = str(block.get("source_asset_key") or paragraph_asset_source_key(paragraph, image_position))
            file_hash = file.sha256_hash or ""

            # Original bytes are the safest fallback when a connector cannot expose a native
            # block/image id. The one-to-one claim prevents duplicate images sharing an asset.
            hash_matches = [asset for asset in candidates if file_hash and asset.source_hash == file_hash]
            asset = hash_matches[0] if len(hash_matches) == 1 else None
            if asset is None:
                asset = next((item for item in candidates if item.source_asset_key == desired_key), None)
            if asset is None and origin == ContentOrigin.MANUAL:
                asset = next(
                    (item for item in candidates if item.paragraph_id == paragraph.id and item.file_id == file.id),
                    None,
                )

            if asset is not None:
                claimed_ids.add(asset.id)
                source_key = asset.source_asset_key or unique_source_key(paragraph, desired_key, file_hash)
            else:
                source_key = unique_source_key(paragraph, desired_key, file_hash)
            plans.append((paragraph, block, image_position, file, origin, source_key, asset))

    active_assets = []
    for paragraph, block, image_position, file, origin, source_key, asset in plans:
        if asset is None:
            asset = ParagraphAsset(
                document_id=paragraph.document_id,
                source_asset_key=source_key,
                origin=origin,
            )
        asset.knowledge_id = paragraph.knowledge_id
        asset.paragraph_id = paragraph.id
        asset.file_id = file.id
        asset.position = image_position
        asset.source_hash = file.sha256_hash
        asset.caption = block["caption"]
        asset.sync_state = SyncState.ACTIVE
        asset.visual_strategy_hash = visual_strategy_hash
        asset.save()
        claimed_ids.add(asset.id)
        block["asset_id"] = str(asset.id)
        block["source_asset_key"] = asset.source_asset_key
        block["caption"] = asset.caption
        block["ocr_text"] = asset.ocr_text
        block["description"] = asset.description
        active_assets.append(asset)

    ParagraphAsset.objects.filter(
        paragraph_id__in=touched_paragraph_ids,
        origin=ContentOrigin.SYNCED,
    ).exclude(id__in=claimed_ids).update(sync_state=SyncState.REMOTE_DELETED)
    for paragraph in paragraphs:
        schema = schemas[paragraph.id]
        paragraph.content_schema = schema
        paragraph.save(update_fields=["content_schema", "update_time"])
    return active_assets


def process_visual_assets(
    assets: Iterable[ParagraphAsset],
    strategy: Dict | None,
    processor: Optional[Callable[[ParagraphAsset, Dict], Dict]] = None,
    workspace_id: str | None = None,
) -> None:
    """Run a model/tool adapter. Errors are isolated per image and never abort document import."""
    assets = list(assets)
    normalized = normalize_document_strategy(strategy)
    visual = normalized["visual"]
    visual_hash = strategy_hashes(normalized)["visual_strategy_hash"]
    resolver_error = ""
    if visual["enabled"] and processor is None:
        try:
            processor = resolve_visual_processor(visual, workspace_id or _get_asset_workspace_id(assets))
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
            asset.description = asset.description or asset.caption
        else:
            try:
                output = processor(asset, visual) or {}
                asset.caption = str(output.get("caption") or asset.caption)
                asset.ocr_text = str(output.get("ocr_text") or asset.ocr_text)
                asset.description = str(output.get("description") or asset.description or asset.caption)
                output_meta = output.get("meta") if isinstance(output.get("meta"), dict) else {}
                asset.meta = {**(asset.meta or {}), **output_meta}
                asset.process_status = AssetProcessStatus.SUCCESS
                asset.process_error = ""
            except Exception as exc:  # Image failure must not interrupt the remaining document.
                asset.process_status = AssetProcessStatus.FAILURE
                asset.process_error = str(exc)[:2000]
                asset.description = asset.description or asset.caption
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


def _get_asset_workspace_id(assets: List[ParagraphAsset]) -> str | None:
    if not assets:
        return None
    asset = assets[0]
    knowledge = getattr(asset, "knowledge", None)
    return str(knowledge.workspace_id) if knowledge is not None else None


def _get_llm_model(model_id, workspace_id: str | None):
    if not workspace_id:
        raise AppApiException(500, _("Workspace id is required for visual model validation"))
    model = get_model_by_id(model_id, workspace_id)
    if model.model_type != ModelTypeConst.IMAGE.name:
        raise AppApiException(500, _("The selected model is not a vision model"))
    return ModelManage.get_model(model_id, lambda _id: get_model(model))


def resolve_visual_processor(
    visual: Dict, workspace_id: str | None = None
) -> Optional[Callable[[ParagraphAsset, Dict], Dict]]:
    if visual.get("strategy") == "model":
        model = _get_llm_model(visual["model_id"], workspace_id)

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
        if not workspace_id:
            raise AppApiException(500, _("Workspace id is required for visual tool validation"))
        authorized_ids = filter_authorized_ids("tool", [str(visual["tool_id"])], workspace_id)
        tool = Tool.objects.filter(id__in=authorized_ids, is_active=True).first()
        if tool is None:
            raise AppApiException(500, _("The selected visual tool does not exist or is not authorized"))

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
    """Create text units for image descriptions and image units when the model supports them."""
    assets = list(
        ParagraphAsset.objects.select_related("file", "paragraph")
        .filter(paragraph_id__in=paragraph_ids, sync_state=SyncState.ACTIVE)
        .order_by("paragraph_id", "position")
    )
    if not assets:
        return 0
    rows = []

    text_assets = []
    text_inputs = []
    for asset in assets:
        text = "\n".join(
            value.strip() for value in (asset.caption, asset.ocr_text, asset.description) if value and value.strip()
        )
        if text:
            text_assets.append(asset)
            text_inputs.append(text)
    if text_inputs:
        text_vectors = embedding_model.embed_documents(text_inputs)
        if len(text_vectors) != len(text_inputs):
            raise AppApiException(500, _("The image description embedding model returned an incomplete result"))
        for asset, text, vector in zip(text_assets, text_inputs, text_vectors):
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
                    search_vector=SearchVector(Value(to_ts_vector(text)), config="simple"),
                    meta={
                        "unit_type": "text",
                        "content_type": "image_description",
                        "asset_id": str(asset.id),
                        "position": asset.position,
                    },
                )
            )

    if embedding_model.supports_image_embedding():
        image_inputs = [_image_data_url(asset) for asset in assets]
        image_vectors = embedding_model.embed_images(image_inputs)
        if len(image_vectors) != len(image_inputs):
            raise AppApiException(500, _("The image embedding model returned an incomplete result"))
        for asset, vector in zip(assets, image_vectors):
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

    if rows:
        Embedding.objects.bulk_create(rows)
    return len(rows)
