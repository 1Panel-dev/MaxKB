"""Standalone image resources for general knowledge bases."""

from pathlib import Path
from typing import Dict, Iterable, List

import uuid_utils.compat as uuid
from common.chunk import text_to_chunk
from common.exception.app_exception import AppApiException
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError

from knowledge.models import (
    AssetProcessStatus,
    ContentOrigin,
    Document,
    DocumentResourceType,
    File,
    FileSourceType,
    Knowledge,
    KnowledgeType,
    Paragraph,
    ParagraphAsset,
    SyncState,
)
from knowledge.services.document_strategy import (
    document_source_hash,
    normalize_document_strategy,
    strategy_hashes,
)
from knowledge.services.incremental_sync import IncrementalDocumentSync
from knowledge.services.paragraph_assets import resolve_visual_processor


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
IMAGE_FORMAT_EXTENSIONS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "WEBP": {".webp"},
    "BMP": {".bmp"},
}


def _preview_meta(file: File) -> Dict:
    return (file.meta or {}).get("image_preview") or {}


def _display_text(file_name: str, preview: Dict) -> str:
    values = [preview.get("caption"), preview.get("ocr_text"), preview.get("description")]
    content = "\n".join(str(value).strip() for value in values if value and str(value).strip()).strip()
    return content or Path(file_name).stem


class ImageDocumentService:
    def __init__(self, workspace_id: str, knowledge_id: str, user_id=None):
        self.workspace_id = workspace_id
        self.knowledge_id = str(knowledge_id)
        self.user_id = user_id

    def get_knowledge(self) -> Knowledge:
        knowledge = QuerySet(Knowledge).filter(id=self.knowledge_id, workspace_id=self.workspace_id).first()
        if knowledge is None:
            raise AppApiException(500, _("Knowledge id does not exist"))
        if knowledge.type != KnowledgeType.BASE:
            raise AppApiException(500, _("Image files are only supported by general knowledge bases"))
        return knowledge

    @staticmethod
    def _validate_image(file, knowledge: Knowledge) -> None:
        extension = Path(file.name).suffix.lower()
        if extension not in SUPPORTED_IMAGE_EXTENSIONS:
            raise AppApiException(
                500,
                _("Unsupported image format. Supported formats: jpg, jpeg, png, webp, bmp"),
            )
        size_limit = min(100, knowledge.file_size_limit)
        if file.size > 1024 * 1024 * size_limit:
            raise AppApiException(
                500,
                _("The maximum size of the uploaded file cannot exceed {}MB").format(size_limit),
            )
        position = file.tell()
        try:
            image = Image.open(file)
            image_format = image.format
            image.verify()
            if extension not in IMAGE_FORMAT_EXTENSIONS.get(image_format, set()):
                raise AppApiException(500, _("The image content does not match its file extension"))
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
            raise AppApiException(500, _("The uploaded file is not a valid image")) from exc
        finally:
            file.seek(position)

    @staticmethod
    def _run_visual_processor(file: File, strategy: Dict, workspace_id: str) -> Dict:
        visual = strategy["visual"]
        if not visual["enabled"]:
            return {
                "caption": "",
                "ocr_text": "",
                "description": "",
                "process_status": AssetProcessStatus.SKIPPED,
                "process_error": "",
                "meta": {},
            }
        try:
            processor = resolve_visual_processor(visual, workspace_id)
            if processor is None:
                raise ValueError("visual processor adapter is unavailable")
            asset = ParagraphAsset(file=file, file_id=file.id, position=1)
            output = processor(asset, visual) or {}
            caption = str(output.get("caption") or "")
            return {
                "caption": caption,
                "ocr_text": str(output.get("ocr_text") or ""),
                "description": str(output.get("description") or caption or Path(file.file_name).stem),
                "process_status": AssetProcessStatus.SUCCESS,
                "process_error": "",
                "meta": output.get("meta") if isinstance(output.get("meta"), dict) else {},
            }
        except Exception as exc:
            original_text = Path(file.file_name).stem
            return {
                "caption": "",
                "ocr_text": "",
                "description": original_text,
                "process_status": AssetProcessStatus.FAILURE,
                "process_error": str(exc)[:2000],
                "meta": {},
            }

    @staticmethod
    def serialize_preview(file: File) -> Dict:
        preview = _preview_meta(file)
        content = _display_text(file.file_name, preview)
        original_size = (file.meta or {}).get("upload_size")
        if original_size is None:
            original_size = (file.meta or {}).get("original_size", file.file_size)
        return {
            "id": str(file.id),
            "preview_id": str(file.id),
            "file_id": str(file.id),
            "name": file.file_name,
            "file_name": file.file_name,
            "file_size": original_size,
            "url": f"./oss/file/{file.id}",
            "caption": preview.get("caption", ""),
            "ocr_text": preview.get("ocr_text", ""),
            "description": preview.get("description", ""),
            "content": content,
            "char_length": len(content),
            "process_status": preview.get("process_status", AssetProcessStatus.PENDING),
            "process_error": preview.get("process_error", ""),
            "doc_strategy": preview.get("doc_strategy", {}),
            "imported": bool(preview.get("imported", False)),
            "document_id": preview.get("document_id"),
        }

    def _get_preview_file(self, preview_id) -> File:
        file = (
            QuerySet(File)
            .filter(
                id=preview_id,
                source_type=FileSourceType.KNOWLEDGE,
                source_id=self.knowledge_id,
            )
            .first()
        )
        if file is None or not _preview_meta(file):
            raise AppApiException(500, _("Image preview does not exist"))
        if _preview_meta(file).get("imported"):
            raise AppApiException(500, _("Image preview has already been imported"))
        return file

    def create_previews(self, files: Iterable, strategy: Dict | None = None) -> List[Dict]:
        knowledge = self.get_knowledge()
        file_list = list(files)
        if not file_list:
            raise AppApiException(500, _("Please upload at least one image"))
        count_limit = min(50, knowledge.file_count_limit)
        if len(file_list) > count_limit:
            raise AppApiException(
                500,
                _("A maximum of {} files can be uploaded at a time").format(count_limit),
            )
        normalized_strategy = normalize_document_strategy(strategy)
        for upload in file_list:
            self._validate_image(upload, knowledge)
        previews = []
        for upload in file_list:
            content = upload.read()
            upload.seek(0)
            file = File(
                id=uuid.uuid7(),
                file_name=upload.name,
                file_size=upload.size,
                source_type=FileSourceType.KNOWLEDGE,
                source_id=self.knowledge_id,
                meta={"knowledge_id": self.knowledge_id, "upload_size": upload.size},
            )
            file.save(content)
            processed = self._run_visual_processor(file, normalized_strategy, self.workspace_id)
            preview = {
                **processed,
                "doc_strategy": normalized_strategy,
                "imported": False,
                "document_id": None,
            }
            meta = {**(file.meta or {}), "image_preview": preview}
            QuerySet(File).filter(id=file.id).update(meta=meta)
            file.meta = meta
            previews.append(self.serialize_preview(file))
        return previews

    def get_preview(self, preview_id) -> Dict:
        self.get_knowledge()
        return self.serialize_preview(self._get_preview_file(preview_id))

    def update_preview(self, preview_id, values: Dict) -> Dict:
        self.get_knowledge()
        file = self._get_preview_file(preview_id)
        file_name = values.get("name", file.file_name)
        if Path(file_name).suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise AppApiException(500, _("The image name must retain a supported file extension"))
        preview = {**_preview_meta(file)}
        for field in ("caption", "ocr_text", "description"):
            if field in values:
                preview[field] = values[field] or ""
        meta = {**(file.meta or {}), "image_preview": preview}
        QuerySet(File).filter(id=file.id).update(file_name=file_name, meta=meta)
        file.file_name = file_name
        file.meta = meta
        return self.serialize_preview(file)

    def delete_preview(self, preview_id) -> bool:
        self.get_knowledge()
        file = self._get_preview_file(preview_id)
        file.delete()
        return True

    @transaction.atomic
    def import_previews(self, preview_ids: Iterable) -> List[str]:
        knowledge = self.get_knowledge()
        ordered_ids = list(dict.fromkeys(str(preview_id) for preview_id in preview_ids))
        if not ordered_ids:
            raise AppApiException(500, _("Please select at least one image preview"))
        preview_files = (
            QuerySet(File)
            .filter(
                id__in=ordered_ids,
                source_type=FileSourceType.KNOWLEDGE,
                source_id=self.knowledge_id,
            )
            .select_for_update()
        )
        files_by_id = {str(file.id): file for file in preview_files}
        if len(files_by_id) != len(ordered_ids):
            raise AppApiException(500, _("One or more image previews do not exist"))

        document_ids = []
        for preview_id in ordered_ids:
            file = files_by_id[preview_id]
            preview = _preview_meta(file)
            if not preview or preview.get("imported"):
                raise AppApiException(500, _("One or more image previews cannot be imported"))
            strategy = normalize_document_strategy(preview.get("doc_strategy"))
            hashes = strategy_hashes(strategy)
            content = _display_text(file.file_name, preview)
            document = Document(
                id=uuid.uuid7(),
                knowledge_id=knowledge.id,
                name=file.file_name,
                char_length=len(content),
                user_id=self.user_id,
                type=KnowledgeType.BASE,
                resource_type=DocumentResourceType.IMAGE,
                doc_strategy=strategy,
                source_hash=document_source_hash([{"title": Path(file.file_name).stem, "content": content}]),
                meta={
                    "source_file_id": str(file.id),
                    "allow_download": True,
                    "image_file_id": str(file.id),
                },
                **hashes,
            )
            document.save()
            paragraph = Paragraph(
                id=uuid.uuid7(),
                document_id=document.id,
                knowledge_id=knowledge.id,
                title=preview.get("caption") or Path(file.file_name).stem,
                content=content,
                chunks=text_to_chunk(content, strategy["split"]["child_length"]),
                content_schema=[
                    {
                        "type": "image",
                        "file_id": str(file.id),
                        "caption": preview.get("caption", ""),
                        "ocr_text": preview.get("ocr_text", ""),
                        "description": preview.get("description", ""),
                    }
                ],
                origin=ContentOrigin.MANUAL,
                position=1,
            )
            paragraph.save()
            ParagraphAsset.objects.create(
                id=uuid.uuid7(),
                knowledge_id=knowledge.id,
                document_id=document.id,
                paragraph_id=paragraph.id,
                file_id=file.id,
                position=1,
                origin=ContentOrigin.MANUAL,
                source_asset_key=f"standalone:{file.sha256_hash or file.id}",
                source_hash=file.sha256_hash,
                caption=preview.get("caption", ""),
                ocr_text=preview.get("ocr_text", ""),
                description=preview.get("description", ""),
                sync_state=SyncState.ACTIVE,
                process_status=preview.get("process_status", AssetProcessStatus.PENDING),
                process_error=preview.get("process_error", ""),
                visual_strategy_hash=hashes["visual_strategy_hash"],
                meta=preview.get("meta") if isinstance(preview.get("meta"), dict) else {},
            )
            IncrementalDocumentSync(document, strategy)._sync_title_questions([paragraph])
            imported_preview = {
                **preview,
                "imported": True,
                "document_id": str(document.id),
                "imported_at": timezone.now().isoformat(),
            }
            file_meta = {**(file.meta or {}), "image_preview": imported_preview}
            QuerySet(File).filter(id=file.id).update(
                source_type=FileSourceType.DOCUMENT,
                source_id=str(document.id),
                meta=file_meta,
            )
            document_ids.append(str(document.id))
        return document_ids
