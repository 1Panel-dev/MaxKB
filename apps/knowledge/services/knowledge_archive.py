"""Lossless knowledge archive data, alongside the legacy Excel representation."""

import copy
import json
import re
from datetime import date, datetime
from pathlib import Path
from uuid import UUID

import uuid_utils.compat as uuid
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from knowledge.models import (
    Document,
    DocumentResourceType,
    DocumentTag,
    File,
    FileSourceType,
    KnowledgeType,
    Paragraph,
    ParagraphAsset,
    Problem,
    ProblemParagraphMapping,
    Tag,
)
from knowledge.serializers.external_retrieval import ExternalServiceSettings
from knowledge.services.knowledge_sync_schedule import normalize_knowledge_sync_setting


ARCHIVE_VERSION = 2
STAT_FIELDS = ("hit_num", "last_hit_time")
DOCUMENT_FIELDS = (
    "id",
    "name",
    "char_length",
    "is_active",
    "type",
    "resource_type",
    "hit_handling_method",
    "directly_return_similarity",
    "meta",
    "doc_strategy",
    "source_hash",
    "split_strategy_hash",
    "visual_strategy_hash",
    "index_strategy_hash",
    "sync_version",
    "last_sync_time",
    *STAT_FIELDS,
)
PARAGRAPH_FIELDS = (
    "id",
    "document_id",
    "title",
    "content",
    "is_active",
    "position",
    "chunks",
    "content_schema",
    "origin",
    "source_key",
    "source_hash",
    "source_snapshot",
    "source_updated_at",
    "local_state",
    "sync_state",
    "anchor_paragraph_id",
    "placement",
    *STAT_FIELDS,
)
ASSET_FIELDS = (
    "id",
    "document_id",
    "paragraph_id",
    "file_id",
    "asset_type",
    "position",
    "origin",
    "source_asset_key",
    "source_hash",
    "caption",
    "ocr_text",
    "description",
    "local_state",
    "sync_state",
    "process_status",
    "process_error",
    "visual_strategy_hash",
    "meta",
    *STAT_FIELDS,
)
PROBLEM_FIELDS = ("id", "content", *STAT_FIELDS)
MAPPING_FIELDS = ("id", "document_id", "paragraph_id", "problem_id", "meta")
TAG_FIELDS = ("id", "key", "value")
RESOURCE_MODELS = {
    "documents": (Document, DOCUMENT_FIELDS),
    "paragraphs": (Paragraph, PARAGRAPH_FIELDS),
    "assets": (ParagraphAsset, ASSET_FIELDS),
    "problems": (Problem, PROBLEM_FIELDS),
    "problem_mappings": (ProblemParagraphMapping, MAPPING_FIELDS),
    "tags": (Tag, TAG_FIELDS),
}
UUID_PATTERN = re.compile(r"(?<![\w-])[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}(?![\w-])")
FILE_URL_PATTERN = re.compile(r"/oss/(?:file|image)/([0-9a-fA-F-]{36})")
FILE_LINK_PATTERN = re.compile(r"(?:https?://[^\s<>\"'()]+?|\.|/[^\s<>\"'()]+?)?/oss/(?:file|image)/([0-9a-fA-F-]{36})")
FILE_KEYS = {"file_id", "image_file_id", "source_file_id"}


class ArchiveJSONEncoder(DjangoJSONEncoder):
    def default(self, value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return super().default(value)


def portable_knowledge_meta(knowledge):
    meta = copy.deepcopy(knowledge.meta or {})
    # Preserve Lark settings without exporting the connection credentials previously omitted.
    if knowledge.type == KnowledgeType.LARK:
        return {key: meta[key] for key in ("doc_strategy", "sync_setting") if key in meta}
    return meta


def _record(obj, fields):
    return {key: copy.deepcopy(getattr(obj, key)) for key in fields}


def _file_ids(value):
    result = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FILE_KEYS and item:
                result.add(str(item))
            else:
                result.update(_file_ids(item))
    elif isinstance(value, list):
        for item in value:
            result.update(_file_ids(item))
    elif isinstance(value, str):
        result.update(FILE_URL_PATTERN.findall(value))
    return result


def export_resources(knowledge, documents, source_files, directory, source_entries):
    """Include image bytes even when optional original document files are not requested."""
    resources = {"documents": [_record(item, DOCUMENT_FIELDS) for item in documents]}
    for key, (model, fields) in RESOURCE_MODELS.items():
        if key != "documents":
            resources[key] = [_record(item, fields) for item in QuerySet(model).filter(knowledge_id=knowledge.id)]
    resources["document_tags"] = list(
        QuerySet(DocumentTag).filter(document__knowledge_id=knowledge.id).values("document_id", "tag_id")
    )
    source_ids = {str(item.id) for item in source_files}
    for document in resources["documents"]:
        if document["resource_type"] != DocumentResourceType.IMAGE:
            meta = document["meta"]
            if str(meta.get("source_file_id")) not in source_ids:
                meta.pop("source_file_id", None)
    required_ids = _file_ids(resources) | _file_ids(portable_knowledge_meta(knowledge)) | source_ids
    files = list(QuerySet(File).filter(id__in=required_ids))
    if {str(item.id) for item in files} != required_ids:
        raise ValidationError("A referenced knowledge file is missing; the archive cannot be exported completely.")
    source_paths = {str(item["id"]): item["zip_path"] for item in source_entries}
    document_ids = {str(item.id) for item in documents}
    resources["files"] = []
    for file in files:
        if not (
            file.source_type == FileSourceType.KNOWLEDGE
            and str(file.source_id) == str(knowledge.id)
            or file.source_type == FileSourceType.DOCUMENT
            and str(file.source_id) in document_ids
        ):
            raise ValidationError("A referenced file does not belong to this knowledge base.")
        file_id = str(file.id)
        zip_path = source_paths.get(file_id, f"oss/file/{file_id}")
        if file_id not in source_paths:
            target = Path(directory) / zip_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file.get_bytes())
        resources["files"].append(
            {
                "id": file_id,
                "file_name": file.file_name,
                "zip_path": zip_path,
                "document_id": str(file.source_id) if str(file.source_id) in document_ids else None,
                # Storage locators are generated by File.save in the destination environment.
                "meta": {
                    key: value
                    for key, value in (file.meta or {}).items()
                    if key in {"image_preview", "mime_type", "content_type"}
                },
            }
        )
    return json.loads(json.dumps(resources, cls=ArchiveJSONEncoder, ensure_ascii=False))


def _ids(rows):
    result = {}
    if not isinstance(rows, list):
        raise ValidationError("Invalid archive resource list.")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValidationError("Invalid archive resource ID.")
        try:
            if str(UUID(row["id"])) != row["id"]:
                raise ValueError("Non-canonical UUID")
        except (ValueError, TypeError) as exc:
            raise ValidationError("Invalid archive resource ID.") from exc
        if row["id"] in result:
            raise ValidationError("Duplicate archive resource ID.")
        result[row["id"]] = row
    return result


def validate_archive(data, archive):
    """Validate all cross-resource references before creating any destination records."""
    if not isinstance(data, dict):
        raise ValidationError("Invalid knowledge archive metadata.")
    setting = data.get("external_service", {})
    if not isinstance(setting, dict) or any(type(value) is not bool for value in setting.values()):
        raise ValidationError("Invalid external service settings.")
    if setting:
        ExternalServiceSettings(data=setting).is_valid(raise_exception=True)
    version = data.get("archive_version")
    if version is None:
        return None
    if type(version) is not int or version != ARCHIVE_VERSION:
        raise ValidationError("Unsupported knowledge archive version.")
    resources = data.get("resources")
    if not isinstance(resources, dict):
        raise ValidationError("Knowledge archive resources are missing.")
    indexes = {key: _ids(resources.get(key)) for key in (*RESOURCE_MODELS, "files")}
    all_ids = [key for index in indexes.values() for key in index]
    if len(all_ids) != len(set(all_ids)) or data.get("source_knowledge_id") in all_ids:
        raise ValidationError("Duplicate archive resource ID.")
    documents, paragraphs = indexes["documents"], indexes["paragraphs"]
    for row in paragraphs.values():
        if row.get("document_id") not in documents:
            raise ValidationError("Paragraph refers to an unknown document.")
        anchor = row.get("anchor_paragraph_id")
        if anchor and (anchor not in paragraphs or paragraphs[anchor]["document_id"] != row["document_id"]):
            raise ValidationError("Invalid paragraph anchor.")
    for kind, target in (("assets", "files"), ("problem_mappings", "problems")):
        field = "file_id" if kind == "assets" else "problem_id"
        for row in indexes[kind].values():
            paragraph = paragraphs.get(row.get("paragraph_id"))
            if paragraph is None or paragraph["document_id"] != row.get("document_id"):
                raise ValidationError("Invalid document/paragraph relationship.")
            if row.get(field) not in indexes[target]:
                raise ValidationError("Unknown related archive resource.")
    if not isinstance(resources.get("document_tags"), list):
        raise ValidationError("Invalid document tags.")
    for row in resources["document_tags"]:
        if (
            not isinstance(row, dict)
            or row.get("document_id") not in documents
            or row.get("tag_id") not in indexes["tags"]
        ):
            raise ValidationError("Invalid document tag relationship.")
    for row in documents.values():
        if row.get("resource_type") not in DocumentResourceType.values or not isinstance(row.get("meta"), dict):
            raise ValidationError("Invalid document resource type or metadata.")
        if (
            row["resource_type"] == DocumentResourceType.IMAGE
            and row["meta"].get("image_file_id") not in indexes["files"]
        ):
            raise ValidationError("Image document has no image file.")
    for row in indexes["files"].values():
        if not isinstance(row.get("file_name"), str) or not isinstance(row.get("meta", {}), dict):
            raise ValidationError("Invalid file metadata.")
        if row.get("document_id") and row["document_id"] not in documents:
            raise ValidationError("File refers to an unknown document.")
        path = row.get("zip_path")
        if not isinstance(path, str) or path not in archive.namelist() or archive.getinfo(path).is_dir():
            raise ValidationError("An archive file is missing.")
    if not _file_ids({key: value for key, value in resources.items() if key != "files"}).issubset(indexes["files"]):
        raise ValidationError("Unknown file reference in knowledge content.")
    meta = data.get("meta", {})
    if not isinstance(meta, dict):
        raise ValidationError("Invalid knowledge metadata.")
    if not _file_ids(meta).issubset(indexes["files"]):
        raise ValidationError("Unknown file reference in knowledge settings.")
    for kind, (model, fields) in RESOURCE_MODELS.items():
        for row in resources[kind]:
            for field in fields:
                if field not in row:
                    raise ValidationError("Missing archive resource field.")
                value = row[field]
                if field in {"meta", "doc_strategy", "source_snapshot"} and not isinstance(value, dict):
                    raise ValidationError("Invalid archive resource metadata.")
                if field in {"chunks", "content_schema"} and not isinstance(value, list):
                    raise ValidationError("Invalid paragraph content structure.")
                if model._meta.get_field(field).get_internal_type() == "DateTimeField":
                    try:
                        model._meta.get_field(field).to_python(value)
                    except Exception as exc:
                        raise ValidationError("Invalid archive timestamp.") from exc
    if "sync_setting" in meta:
        setting = meta["sync_setting"]
        if setting is not None and (not isinstance(setting, dict) or type(setting.get("enabled", False)) is not bool):
            raise ValidationError("Invalid synchronization settings.")
        try:
            normalize_knowledge_sync_setting(setting)
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValidationError("Invalid synchronization settings.") from exc
    return resources


def remap_references(value, id_map):
    """Remap structured IDs and IDs embedded in Markdown, snapshots and workflow inputs."""
    if isinstance(value, dict):
        return {key: remap_references(item, id_map) for key, item in value.items()}
    if isinstance(value, list):
        return [remap_references(item, id_map) for item in value]
    if isinstance(value, str):
        value = FILE_LINK_PATTERN.sub(
            lambda match: f"./oss/file/{id_map[match.group(1)]}" if match.group(1) in id_map else match.group(),
            value,
        )
        return UUID_PATTERN.sub(lambda match: str(id_map.get(match.group(), match.group())), value)
    return value


def restore_resources(knowledge, data, archive):
    resources = data["resources"]
    id_map = {row["id"]: uuid.uuid7() for key in (*RESOURCE_MODELS, "files") for row in resources[key]}
    if data.get("source_knowledge_id"):
        id_map[data["source_knowledge_id"]] = knowledge.id
    for row in resources["files"]:
        document_id = id_map.get(row.get("document_id"))
        file = File(
            id=id_map[row["id"]],
            file_name=row["file_name"],
            source_type=FileSourceType.DOCUMENT if document_id else FileSourceType.KNOWLEDGE,
            source_id=str(document_id or knowledge.id),
            meta=remap_references(row.get("meta", {}), id_map),
        )
        file.save(archive.read(row["zip_path"]))
    # Parent records precede their dependent records. Embedding/task state is regenerated later.
    for key in ("documents", "paragraphs", "problems", "problem_mappings", "assets", "tags"):
        model, fields = RESOURCE_MODELS[key]
        records = []
        for row in resources[key]:
            values = {field: remap_references(row[field], id_map) for field in fields if field in row}
            for field in fields:
                if field in values and model._meta.get_field(field).get_internal_type() == "DateTimeField":
                    values[field] = model._meta.get_field(field).to_python(values[field])
            if key == "documents":
                values["user_id"] = knowledge.user_id
            records.append(model(**values, knowledge_id=knowledge.id))
        if records:
            QuerySet(model).bulk_create(records, batch_size=1000)
    tags = [
        DocumentTag(document_id=id_map[row["document_id"]], tag_id=id_map[row["tag_id"]])
        for row in resources["document_tags"]
    ]
    if tags:
        QuerySet(DocumentTag).bulk_create(tags, batch_size=1000)
    knowledge.meta = remap_references(knowledge.meta, id_map)
    knowledge.save(update_fields=["meta"])
    return id_map
