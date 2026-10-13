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

Synchronization without embedding publishes `celery:process_paragraph_visual_assets` after commit
to recognize the images independently. Synchronization success means the source snapshot is saved;
recognition status is available on the paragraph assets, while embedding status tracks indexing.
Image extraction, file storage and source reconciliation still occur in the import/sync transaction;
the external vision model or tool runs in the worker.
