# Knowledge document processing

Document imports save paragraphs, original inline images, and `ParagraphAsset` records
in the import transaction. With visual enhancement enabled, image assets remain `pending`;
the request does not call the vision model or tool.

The existing embedding job is published with `transaction.on_commit`. In the worker,
`process_pending_visual_assets` enhances pending images using the document strategy and knowledge
workspace before reading the paragraph text for indexing. Results update the paragraph image
blocks; standalone images also update their paragraph text and chunks. `embed_paragraph_assets`
indexes the image descriptions. Completed assets are reused when embeddings are rebuilt.
A failed image retains its existing description or caption and does not stop the remaining images.

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
系统资源管理和共享资源管理沿用上述路径后缀、请求及处理流程，
各自的知识库路径前缀和权限由对应功能模块说明。

图片预览与文档分段预览使用相同的文档结构：`name`、`source_file_id`、`doc_strategy`
和 `content: [{"title": "<文件名（不含扩展名）>", "content": "<预览正文>"}]`。
每张图片对应一个分段，正文由图片标题、OCR 文字和描述组成，无识别文字时使用文件名（不含扩展名）。
图片预览额外保留 `preview_id`、`url`、`caption`、`ocr_text`、`description`、
`process_status`、`process_error` 等字段；创建预览返回文档数组，查询和修改预览返回单个文档。

文档列表、分页接口通过 `resource_type=image` 查询图片，省略该参数时仍查询普通文档。
启用视觉增强后，生成预览会调用所选模型或工具，完成识别后直接返回 `success` 或 `failure`，
正文分段包含识别结果，客户端无需轮询；关闭视觉增强返回 `skipped`。
不经过预览直接导入时，图片识别仍由 Celery 向量化任务处理，状态及导入时序见上文。
