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

Standalone image uploads save editable previews and return `process_status: pending` immediately
when visual enhancement is enabled. After commit, `celery:process_image_preview` recognizes
each image. Clients can query the existing `document/image/preview/<preview_id>` GET endpoint
until the status becomes `success` or `failure`. Disabled enhancement returns `skipped`.
An enqueue failure is recorded on the preview instead of leaving it permanently pending.

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
| POST | `/document/image/preview` | 上传图片并生成预览 |
| GET | `/document/image/preview/<preview_id>` | 查询预览及异步识别状态 |
| PUT | `/document/image/preview/<preview_id>` | 修改 `name`、`caption`、`ocr_text` 或 `description` |
| DELETE | `/document/image/preview/<preview_id>` | 删除预览 |
| PUT | `/document/image/batch_create` | 批量导入图片文档 |

上传使用 multipart，`file` 支持多个文件，`doc_strategy` 为可选 JSON；批量导入提交
`{"preview_ids": [...]}`。系统资源管理和共享资源管理沿用上述路径后缀、请求及处理流程，
各自的知识库路径前缀和权限由对应功能模块说明。

文档列表、分页接口通过 `resource_type=image` 查询图片，省略该参数时仍查询普通文档。
启用视觉增强后，上传先返回 `process_status: pending`，客户端轮询预览详情直到识别完成；
异步识别依赖 Celery task 服务，状态及导入时序见上文。
