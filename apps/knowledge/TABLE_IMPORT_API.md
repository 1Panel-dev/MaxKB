# Import tables and QA from uploaded files

The endpoints use the existing API base path and document-create permissions for each scope:

| Scope | Endpoint prefix |
| --- | --- |
| Workspace | `workspace/{workspace_id}/knowledge/{knowledge_id}/document` |
| System shared knowledge | `system/shared/knowledge/{knowledge_id}/document` |
| System resource knowledge | `system/resource/knowledge/{knowledge_id}/document` |

Append `/table_by_file_ids` for tables or `/qa_by_file_ids` for QA, and send a POST request.
System resource imports resolve the workspace from the knowledge base; shared imports use
the existing shared workspace context. Workspace shared access remains read-only.

Send `Content-Type: application/json` and a nonempty list of uploaded file UUIDs:

```json
{
  "file_id_list": ["019a0a00-0000-7000-8000-000000000001"]
}
```

These are `File` IDs, not existing `Document` IDs. The upload API `POST oss/file`
returns `./oss/file/{file_id}`; take the final path segment for this request.
Files may be temporary uploads owned by the current user, or files already associated
with the target knowledge base. Other source types and other knowledge bases are rejected.

The table endpoint supports the same CSV/XLS/XLSX parsers as `document/table`.
The QA endpoint supports CSV/XLS/XLSX/ZIP through the existing `document/qa` parsers,
including question associations and embedded images. Both endpoints use the existing
file size limits, document creation, and embedding processing. They preserve request order and reject
missing, invalid, duplicate, or inaccessible IDs. Uploaded source IDs are reused and
associated with the knowledge base so temporary-file cleanup does not remove them.
The response uses the existing success envelope and created-document list.

The original multipart `document/table` and `document/qa` endpoints remain available.
After upload, the frontend calls `document/table_by_file_ids` or `document/qa_by_file_ids`
with the same JSON body shown above instead of posting the file bytes again.
