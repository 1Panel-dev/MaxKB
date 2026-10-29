# Knowledge document processing

## Backend translations

User-facing validation errors must use Django translation functions with literal message IDs.
Keep the `zh_CN`, `zh_Hant`, and `en_US` catalogs in `apps/locales/` in sync, including format
placeholders. Translate service errors at their source before converting them to serializer errors.
Run `uv run python apps/manage.py test knowledge.tests.test_i18n` to check catalog coverage and
language-dependent validation messages. The tests compile catalogs in a temporary directory.
After changing catalogs, run `uv run python apps/manage.py compilemessages` from the repository root
and restart the web and task services to reload translations.

## Document processing

Document imports save paragraphs, original inline images, and `ParagraphAsset` records
in the import transaction. With visual enhancement enabled, image assets remain `pending`;
the request does not call the vision model or tool.

The existing embedding job is published with `transaction.on_commit`. In the worker,
`process_pending_visual_assets` enhances pending images using the document strategy and knowledge
workspace before reading the paragraph text for indexing. For ordinary documents in general knowledge
bases, successful inline image recognition also writes the description into the Markdown alt text:
`![description](./oss/file/<file_id>)`.
The image URL and surrounding text are preserved; description line breaks become spaces and
brackets/backslashes are escaped. The image blocks, paragraph chunks and document character count
are updated together without changing source fingerprints. Failed or skipped recognition leaves
the original Markdown intact. Standalone images update their paragraph text and chunks. `embed_paragraph_assets`
indexes the image descriptions. Completed assets are reused when embeddings are rebuilt.
A failed image retains its existing description or caption and does not stop the remaining images.

Before paragraph text is embedded, inline image Markdown is replaced with its description;
image URLs, file IDs and filename-only alt text are excluded. Image-containing text is split
again using the document strategy's child length, so old chunks containing partial image
links are not reused. Stored Markdown and original images remain available for display.
After upgrading, rebuild embeddings for affected documents to replace existing link-based
text vectors. Image vectors and image-description vectors are still indexed separately.

The `document/image/preview` POST endpoint saves editable previews in a short transaction,
then completes visual enhancement before responding. Model and tool strategies return the
recognized caption, OCR text and description in the initial response with `process_status: success`.
Each failed image returns `failure` and `process_error` while other images keep their results;
disabled enhancement returns `skipped`. Recognition runs after releasing the preparation transaction's
file locks, and preview generation does not require a Celery worker.

The existing `celery:process_image_preview` task remains available for asynchronous preview callers.
Clients can query saved results through `document/image/preview/<preview_id>`.

Preview edits are retained when recognition finishes, including explicitly cleared fields.
If a pending preview is imported, its asset is recognized by the embedding worker, and the
preview worker discards its late result. Results for deleted previews are also discarded.
No external model call holds a preview row lock.

Saving edited paragraph content synchronizes inline image references into `content_schema`
and `ParagraphAsset` before returning the paragraph. Standalone image documents retain their
original image asset and its recognition results. New or replaced images use the document's
visual strategy; inline recognition in general knowledge base documents updates their descriptions
while preserving surrounding edited text.
For standalone image documents, recognition updates structured metadata without replacing edited paragraph text.
Removing an inline image also removes its asset record and image embeddings in the same transaction.
The returned `assets` and `content_schema` reflect the remaining images; underlying files are retained
because other paragraphs may still reference them.

Run both the web service and the Celery task service. Import completion means the source
content is saved; the document's embedding status indicates when indexing has finished.

Inline image deferral applies to all documents imported through `DocumentSerializers.Create.save`
and `DocumentSerializers.Batch.batch_save`, including Web, Lark and workflow output. Web document
sync, Lark reimport/sync, and workflow snapshot reconciliation use `defer_visual_assets` as well.
Changed images and visual strategy changes reset assets to `pending`, retaining prior descriptions
until recognition completes. Unchanged documents keep their completed recognition results.
Worker write-back checks the image file/hash, paragraph location and visual strategy under short
paragraph/asset row locks, acquired in the same order as sync. Results from an older sync or a deleted
image are discarded instead of overwriting the current image. The model/tool call runs before those
locks are acquired. Workflow reconciliation uses the incoming document's visual strategy.

Synchronization without embedding publishes `celery:process_paragraph_visual_assets` after commit
to recognize the images independently. Synchronization success means the source snapshot is saved;
recognition status is available on the paragraph assets, while embedding status tracks indexing.
Image extraction, file storage and source reconciliation still occur in the import/sync transaction;
the external vision model or tool runs in the worker.

Inline images from document imports, Web, Lark and workflow synchronization share the same ownership
rules. Once paragraph assets are saved, their files use `source_type=PARAGRAPH` and a referencing
paragraph's ID as `source_id`. Original source documents (`meta.source_file_id`) and standalone image
documents retain their document ownership.
Document previews (`split` and `split_by_file_ids`) keep source uploads temporary. Images extracted
during preview are also temporary, with uploader and preview knowledge context in metadata; only
images referenced by saved paragraphs from that uploader and knowledge base acquire paragraph
ownership. Abandoned previews remain eligible for the normal temporary-file cleanup job.
`ParagraphAsset` retains every document/paragraph reference; shared images keep the same file ID and
URL across syncs. Deleting the owning paragraph transfers ownership to another referencing paragraph,
or deletes the file when no paragraph assets remain. Rechunking and replacement temporarily stage
reused images before deleting old paragraphs, then bind them to the saved replacement paragraphs in
the same transaction. Deleting temporary workflow documents also preserves images referenced by the
stable document. The Web cache resolves paragraph-owned images through their asset records within the
same knowledge base. Unchanged Web, Lark and workflow document syncs also transfer legacy image files
without changing paragraph content or recognition results.
Moving shared images to another knowledge base separates their file ownership records while
reusing the stored bytes, so access checks and later paragraph deletion remain independent.

## Paragraph deletion

Single and batch deletion physically remove manually created paragraphs. Source-derived paragraphs
retain their records and source metadata with `local_state=deleted` and `is_active=false`, so
incremental synchronization can recognize local deletions and source conflicts. Both paths remove
the deleted paragraphs' embeddings.

Paragraph lists, pagination totals and document `paragraph_count` exclude `local_state=deleted`.
Document character-length recalculation also excludes these rows. Disabled paragraphs that have
not been deleted remain visible and counted; synchronization continues to read retained deleted rows.

Problem association results and their paragraph counts also exclude deleted paragraphs; new single
or batch associations to them are rejected. Existing mappings are retained for synchronization.
Document and knowledge Excel exports, including single/batch content ZIPs, omit deleted paragraphs
and their attachments. Knowledge migration archives omit them from Excel but retain them in
`knowledge.json` resources, including source snapshots and related files, to preserve deletion state
after import. Optional original source downloads remain the original uploaded files.

Vector, keyword and hybrid search exclude deleted paragraphs before selecting candidates and applying
Top N, even if old embeddings remain or a background task recreates them. Paragraph loading for hit
tests, workflow retrieval and REST/MCP retrieval rechecks deletion state before returning content.

## 图片文档接口

通用知识库支持将图片预览导入为独立图片文档。工作空间接口的知识库路径前缀为
`/workspace/<workspace_id>/knowledge/<knowledge_id>`，位于 Admin API 路径下
（默认 `/admin/api`）。

| 方法 | 路径后缀 | 用途 |
| --- | --- | --- |
| POST | `/document/image/preview` | 复用已上传图片生成预览 |
| GET | `/document/image/preview/<preview_id>` | 查询预览及识别状态 |
| PUT | `/document/image/preview/<preview_id>` | 修改 `name`、`caption`、`ocr_text` 或 `description` |
| DELETE | `/document/image/preview/<preview_id>` | 删除预览 |
| PUT | `/document/image/batch_create` | 批量导入图片文档 |

预览使用 JSON：`{"file_id_list": ["<uploaded-file-uuid>"], "doc_strategy": {...}}`，
文件 ID 必填、不可重复且最多 50 个，同时受知识库文件数量限制。仅接受当前用户的临时文件
或当前知识库的文件；校验实际图片格式和大小后复用原文件，不重复存储。`doc_strategy` 可选。批量导入提交
`{"file_id_list": [...], "doc_strategy": {...}}`，其中 `doc_strategy` 可选。
`file_id_list` 支持当前用户上传的临时图片 ID 和当前知识库已生成预览的图片文件 ID，可不经过预览直接导入。
直接导入校验整批图片的权限、格式、大小和数量后创建图片文档，视觉增强由导入后的向量化任务执行；
已有预览保留其处理策略、识别结果和编辑，不被请求中的 `doc_strategy` 覆盖。
生成预览保留上传文件的临时 `source_type` 和 `source_id`，不提前绑定知识库；图片识别结果及
本次预览的知识库上下文暂存在 `meta.image_preview`。查询、编辑、删除和识别任务校验上传用户
及预览上下文；正式导入成功后才将文件绑定到新文档。未保存的预览仍按原临时文件期限清理。
已有的知识库归属预览继续兼容读取和导入，本次变更不自动调整历史文件归属。

图片扩展名和实际内容均须属于 JPG/JPEG、PNG、WEBP、BMP 支持范围。有效图片的扩展名与实际格式
不一致时，预览和直接导入会按实际格式纠正保存的文件名（例如 PNG 内容的 `神奇图片.jpg` 保存为
`神奇图片.png`），保留原始图片字节和已有文件 ID，保证下载及视觉识别使用正确的 MIME 类型。
非图片、损坏图片以及伪装成支持格式的 GIF/TIFF 等文件仍会被拒绝。

系统资源管理和共享资源管理沿用上述路径后缀、请求及处理流程，
各自的知识库路径前缀和权限由对应功能模块说明。

生成图片预览的响应仅包含 `name`、`source_file_id`、`resource_type: "image"`、`doc_strategy`
和 `content: [{"title": "<文件名（不含扩展名）>", "content": "<预览正文>"}]`。
每张图片对应一个分段，正文由图片标题、OCR 文字和描述组成，无识别文字时使用文件名（不含扩展名）。
创建预览返回文档数组，导入时使用 `source_file_id` 填充 `file_id_list`。
查询和修改单个预览时，路径中的 `preview_id` 使用 `source_file_id`，响应继续包含
`caption`、`ocr_text`、`description`、`process_status`、`process_error` 等识别详情。

文档列表、分页接口通过 `resource_type=image` 查询图片，省略该参数时仍查询普通文档。
启用视觉增强后，生成预览会调用所选模型或工具，完成识别后返回正文分段，客户端无需轮询；
关闭视觉增强或识别失败时，正文回退到文件名（不含扩展名）。识别状态保存在预览元数据中。
不经过预览直接导入时，图片识别仍由 Celery 向量化任务处理，状态及导入时序见上文。

召回测试 `/hit_test` 的每条分段结果包含 `document_resource_type`，取自所属文档的 `resource_type`：
`image` 表示图片文档，`document` 表示普通文档。工作空间、系统资源管理和系统共享资源的召回测试
使用相同字段；此字段与命中向量类型无关，普通文档中的插图命中仍返回 `document`。
图片文档的结果额外包含 `document_image_id`，取自文档的 `meta.source_file_id`，用于通过现有文件接口显示原图。
该字段不依赖命中的是文本还是图片向量；普通文档以及缺少原文件引用的图片文档返回 `null`。
每条结果同时返回所属知识库当前的 `knowledge_type`，沿用 `KnowledgeType` 数字枚举：
`0` 通用、`1` Web 站点、`2` 飞书、`3` 语雀、`4` 工作流。

上述三个来源字段也适用于问题关联段落、工作流知识库检索的 `paragraph_list`、
文档检索节点的 `document_items`、聊天记录查询的来源 `paragraph_list`，以及 REST/MCP 外部检索的 `hits`。
知识库类型取自所属知识库，图片 ID 取自所属文档的原图引用，与命中向量或普通文档内的插图无关。
段落来源通过一次批量查询补齐；已包含完整来源字段的聊天快照直接复用，旧快照缺少字段时在读取时补齐，
不修改已保存的聊天记录。隐藏来源时不加载这些元数据。文档已删除时保留快照中的已知字段，缺少的图片 ID 为 `null`。


## 工作空间知识库权限

工作空间知识库的图片、定时同步、文档处理策略、外部服务和设置分别使用独立子组，
MCP 配置和导出 Skills 使用独立权限位，命名均以 `KNOWLEDGE_` 为前缀。
图片提供查看、创建、编辑、删除、下载原文档、生成问题、向量化、迁移、标签设置、替换原文档、分词索引。
权限在 `permissions.py` 统一组合工作空间、知识库资源、管理员和显式所有者授权。

- 文档和图片共用的单项操作从数据库确定实际资源类型；混合批次须同时满足两种类型的权限。
  列表以 `resource_type` 区分文档和图片。图片批量操作缺少该参数时根据所选 ID 推断类型，
  要求单一类型的业务操作仍拒绝混合提交。
- `sync_setting` GET／PUT 和 `sync_log` 使用定时同步查看／编辑权限；
  `external_service` GET／PUT 使用外部服务查看／编辑权限。
- 知识库详情 GET 的 `section=setting/document_strategy` 分别要求设置／文档处理策略查看权限。
  普通详情过滤未授权的配置元数据；PUT 按提交字段校验权限，保留未提交的独立配置。
  飞书的专用设置更新入口遵循相同字段权限规则。
- GET `/<knowledge_id>/mcp_config` 只返回 MCP 配置，要求 `KNOWLEDGE_MCP_CONFIG`。
  `KNOWLEDGE_EXPORT_SKILLS` 已可分配；知识库尚无导出 Skills 的接口或页面入口。

工作空间与系统资源知识库均按 `group + sub_group` 隔离位图，保持已保存权限 ID 和位序不变。
权限缓存使用 V3 命名空间。自定义角色需明确勾选新增权限；资源授权的 VIEW 包含新增查看权限，
MANAGE 包含新增维护权限，系统管理员、当前空间管理员和显式所有者沿用既有访问能力。
