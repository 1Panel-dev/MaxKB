"""Standalone image resources for general knowledge bases."""

from functools import partial
from pathlib import Path
from typing import Dict, Iterable, List

import uuid_utils.compat as uuid
from common.chunk import text_to_chunk
from common.exception.app_exception import AppApiException
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q, QuerySet
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
from knowledge.services import validate_knowledge_file_size
from knowledge.services.document_strategy import (
    document_source_hash,
    normalize_document_strategy,
    strategy_hashes,
)
from knowledge.services.incremental_sync import IncrementalDocumentSync
from knowledge.services.paragraph_assets import resolve_visual_processor


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
IMAGE_FORMAT_EXTENSIONS = {
    "JPEG": (".jpg", ".jpeg"),
    "PNG": (".png",),
    "WEBP": (".webp",),
    "BMP": (".bmp",),
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
    def _validate_image(file, knowledge: Knowledge) -> str:
        """Validate the bytes and return a filename matching the detected format."""
        extension = Path(file.name).suffix.lower()
        if extension not in SUPPORTED_IMAGE_EXTENSIONS:
            raise AppApiException(
                500,
                _("Unsupported image format. Supported formats: jpg, jpeg, png, webp, bmp"),
            )
        validate_knowledge_file_size(knowledge, [file])
        position = file.tell()
        try:
            image = Image.open(file)
            image_format = image.format
            image.verify()
            extensions = IMAGE_FORMAT_EXTENSIONS.get(image_format)
            if not extensions:
                raise AppApiException(
                    500,
                    _("Unsupported image format. Supported formats: jpg, jpeg, png, webp, bmp"),
                )
            # Downloads and vision requests infer MIME from the stored filename.
            if extension not in extensions:
                return str(Path(file.name).with_suffix(extensions[0]))
            return file.name
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
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
                raise ValueError(_("visual processor adapter is unavailable"))
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
            "source_file_id": str(file.id),
            "resource_type": DocumentResourceType.IMAGE,
            "name": file.file_name,
            "file_name": file.file_name,
            "file_size": original_size,
            "url": f"./oss/file/{file.id}",
            "caption": preview.get("caption", ""),
            "ocr_text": preview.get("ocr_text", ""),
            "description": preview.get("description", ""),
            "content": [{"title": Path(file.file_name).stem, "content": content}],
            "char_length": len(content),
            "process_status": preview.get("process_status", AssetProcessStatus.PENDING),
            "process_error": preview.get("process_error", ""),
            "doc_strategy": preview.get("doc_strategy", {}),
            "imported": bool(preview.get("imported", False)),
            "document_id": preview.get("document_id"),
        }

    def _file_access_filter(self, *, preview=False) -> Q:
        scope = Q(source_type=FileSourceType.KNOWLEDGE, source_id=self.knowledge_id)
        if self.user_id is not None:
            temporary = Q(
                source_type__in=[
                    FileSourceType.TEMPORARY_30_MINUTE,
                    FileSourceType.TEMPORARY_120_MINUTE,
                    FileSourceType.TEMPORARY_1_DAY,
                ],
                meta__user_id=str(self.user_id),
            )
            if preview:
                temporary &= Q(meta__image_preview__knowledge_id=self.knowledge_id)
            scope |= temporary
        return scope

    def _get_preview_file(self, preview_id, *, for_update=False) -> File:
        files = QuerySet(File).filter(self._file_access_filter(preview=True), id=preview_id)
        file = (files.select_for_update() if for_update else files).first()
        if file is None or not _preview_meta(file):
            raise AppApiException(500, _("Image preview does not exist"))
        if _preview_meta(file).get("imported"):
            raise AppApiException(500, _("Image preview has already been imported"))
        return file

    def _complete_preview(self, preview_id, processed: Dict, *, expected_strategy: Dict | None = None) -> None:
        # Lock only the short write-back, never the external vision call. Import/edit/delete
        # may happen while recognition is running, so reload the current preview first.
        with transaction.atomic():
            file = (
                QuerySet(File).filter(self._file_access_filter(preview=True), id=preview_id).select_for_update().first()
            )
            if file is None:
                return
            preview = _preview_meta(file)
            if not preview or preview.get("imported") or preview.get("process_status") != AssetProcessStatus.PENDING:
                return
            if (
                expected_strategy is not None
                and normalize_document_strategy(preview.get("doc_strategy")) != expected_strategy
            ):
                return
            updated = {**preview, **processed}
            for field in preview.get("edited_fields", []):
                if field in ("caption", "ocr_text", "description"):
                    updated[field] = preview.get(field, "")
            QuerySet(File).filter(id=file.id).update(meta={**(file.meta or {}), "image_preview": updated})

    def process_preview(self, preview_id) -> None:
        self.get_knowledge()
        file = QuerySet(File).filter(self._file_access_filter(preview=True), id=preview_id).first()
        if file is None:
            return
        preview = _preview_meta(file)
        if not preview or preview.get("imported") or preview.get("process_status") != AssetProcessStatus.PENDING:
            return
        strategy = normalize_document_strategy(preview.get("doc_strategy"))
        self._complete_preview(
            preview_id, self._run_visual_processor(file, strategy, self.workspace_id), expected_strategy=strategy
        )

    def _enqueue_preview(self, preview_id) -> None:
        from knowledge.tasks import process_image_preview

        try:
            process_image_preview.delay(
                self.workspace_id,
                self.knowledge_id,
                preview_id,
                str(self.user_id) if self.user_id is not None else None,
            )
        except Exception as exc:
            self._complete_preview(
                preview_id,
                {"process_status": AssetProcessStatus.FAILURE, "process_error": str(exc)[:2000]},
            )

    @transaction.atomic
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
        file_names = [self._validate_image(upload, knowledge) for upload in file_list]
        previews = []
        for upload, file_name in zip(file_list, file_names):
            content = upload.read()
            upload.seek(0)
            file = File(
                id=uuid.uuid7(),
                file_name=file_name,
                file_size=upload.size,
                source_type=FileSourceType.TEMPORARY_120_MINUTE,
                source_id=FileSourceType.TEMPORARY_120_MINUTE,
                meta={"user_id": str(self.user_id), "upload_size": upload.size},
            )
            file.save(content)
            previews.append(self._initialize_preview(file, normalized_strategy))
        return previews

    def _initialize_preview(self, file: File, strategy: Dict, *, enqueue=True) -> Dict:
        if strategy["visual"]["enabled"]:
            processed = {
                "caption": "",
                "ocr_text": "",
                "description": "",
                "process_status": AssetProcessStatus.PENDING,
                "process_error": "",
                "meta": {},
            }
        else:
            processed = self._run_visual_processor(file, strategy, self.workspace_id)
        preview = {
            **processed,
            "knowledge_id": self.knowledge_id,
            "doc_strategy": strategy,
            "imported": False,
            "document_id": None,
        }
        meta = {**(file.meta or {}), "image_preview": preview}
        QuerySet(File).filter(id=file.id).update(meta=meta)
        file.meta = meta
        if enqueue and strategy["visual"]["enabled"]:
            transaction.on_commit(partial(self._enqueue_preview, str(file.id)), robust=True)
        return self.serialize_preview(file)

    def _get_uploaded_image_files(self, ordered_ids: List[str]) -> Dict[str, File]:
        files = {
            str(file.id): file
            for file in QuerySet(File).filter(self._file_access_filter(), id__in=ordered_ids).select_for_update()
        }
        if len(files) != len(ordered_ids):
            raise AppApiException(500, _("File does not exist or no permission to access"))
        return files

    @transaction.atomic
    def create_previews_by_file_ids(
        self, file_ids: Iterable, strategy: Dict | None = None, *, enqueue=True
    ) -> List[Dict]:
        knowledge = self.get_knowledge()
        ordered_ids = [str(file_id) for file_id in file_ids]
        if not ordered_ids or len(ordered_ids) > min(50, knowledge.file_count_limit):
            raise AppApiException(500, _("Invalid number of image files"))
        files = self._get_uploaded_image_files(ordered_ids)
        source_files = [files[file_id] for file_id in ordered_ids]
        normalized_strategy = normalize_document_strategy(strategy)
        file_names = {}
        # Validate the whole batch before updating previews or scheduling recognition.
        for file in source_files:
            if _preview_meta(file).get("imported"):
                raise AppApiException(500, _("Image preview has already been imported"))
            with ContentFile(file.get_bytes(), name=file.file_name) as content:
                file_names[file.id] = self._validate_image(content, knowledge)
        previews = []
        for file in source_files:
            # Previewing does not transfer ownership or exempt temporary uploads from cleanup.
            QuerySet(File).filter(id=file.id).update(file_name=file_names[file.id])
            file.file_name = file_names[file.id]
            previews.append(self._initialize_preview(file, normalized_strategy, enqueue=enqueue))
        return previews

    def generate_previews_by_file_ids(self, file_ids: Iterable, strategy: Dict | None = None) -> List[Dict]:
        previews = self.create_previews_by_file_ids(file_ids, strategy, enqueue=False)
        # Complete recognition after the preparation transaction releases its file locks.
        for index, preview in enumerate(previews):
            if preview["process_status"] == AssetProcessStatus.PENDING:
                self.process_preview(preview["preview_id"])
                previews[index] = self.get_preview(preview["preview_id"])
        return previews

    def get_preview(self, preview_id) -> Dict:
        self.get_knowledge()
        return self.serialize_preview(self._get_preview_file(preview_id))

    @transaction.atomic
    def update_preview(self, preview_id, values: Dict) -> Dict:
        self.get_knowledge()
        file = self._get_preview_file(preview_id, for_update=True)
        file_name = values.get("name", file.file_name)
        if Path(file_name).suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise AppApiException(500, _("The image name must retain a supported file extension"))
        preview = {**_preview_meta(file)}
        edited_fields = set(preview.get("edited_fields", []))
        for field in ("caption", "ocr_text", "description"):
            if field in values:
                preview[field] = values[field] or ""
                edited_fields.add(field)
        preview["edited_fields"] = sorted(edited_fields)
        meta = {**(file.meta or {}), "image_preview": preview}
        QuerySet(File).filter(id=file.id).update(file_name=file_name, meta=meta)
        file.file_name = file_name
        file.meta = meta
        return self.serialize_preview(file)

    @transaction.atomic
    def delete_preview(self, preview_id) -> bool:
        self.get_knowledge()
        file = self._get_preview_file(preview_id, for_update=True)
        file.delete()
        return True

    @transaction.atomic
    def import_previews(self, file_ids: Iterable, strategy: Dict | None = None) -> List[str]:
        knowledge = self.get_knowledge()
        ordered_ids = list(dict.fromkeys(str(file_id) for file_id in file_ids))
        if not ordered_ids:
            raise AppApiException(500, _("Please select at least one image preview"))
        if len(ordered_ids) > min(50, knowledge.file_count_limit):
            raise AppApiException(500, _("Invalid number of image files"))
        files_by_id = self._get_uploaded_image_files(ordered_ids)
        normalized_strategy = normalize_document_strategy(strategy)
        file_names = {}
        # Direct imports use uploaded images; validate the entire batch before creating documents.
        for file in files_by_id.values():
            preview = _preview_meta(file)
            if preview.get("imported"):
                raise AppApiException(500, _("One or more image previews cannot be imported"))
            if preview.get("knowledge_id", self.knowledge_id) != self.knowledge_id:
                raise AppApiException(500, _("File does not exist or no permission to access"))
            if not preview:
                with ContentFile(file.get_bytes(), name=file.file_name) as content:
                    file_names[file.id] = self._validate_image(content, knowledge)

        document_ids = []
        for file_id in ordered_ids:
            file = files_by_id[file_id]
            preview = _preview_meta(file)
            if not preview:
                file.file_name = file_names[file.id]
                # The embedding worker processes pending assets after import; no preview job is needed.
                self._initialize_preview(file, normalized_strategy, enqueue=False)
                preview = _preview_meta(file)
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
                title=Path(file.file_name).stem,
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
                meta={
                    **(preview.get("meta") if isinstance(preview.get("meta"), dict) else {}),
                    "visual_edited_fields": preview.get("edited_fields", []),
                },
            )
            IncrementalDocumentSync(document, strategy)._sync_title_questions([paragraph])
            imported_preview = {
                **preview,
                "imported": True,
                "document_id": str(document.id),
                "imported_at": timezone.now().isoformat(),
            }
            file_meta = {**(file.meta or {}), "knowledge_id": self.knowledge_id, "image_preview": imported_preview}
            QuerySet(File).filter(id=file.id).update(
                source_type=FileSourceType.DOCUMENT,
                source_id=str(document.id),
                file_name=file.file_name,
                meta=file_meta,
            )
            document_ids.append(str(document.id))
        return document_ids
