/** Stay under common proxy limits and Django's historical 2.5 MiB default. */
export const DOCUMENT_BATCH_MAX_BYTES = Math.floor(1.5 * 1024 * 1024)

export function jsonUtf8ByteLength(value: unknown): number {
  const json = JSON.stringify(value)
  return new TextEncoder().encode(json ?? 'null').length
}

/**
 * Split a batch_create document list so each JSON body stays near maxBytes.
 * A single document larger than maxBytes is still one chunk.
 * Non-array payloads are returned unchanged as a single request body.
 */
export function chunkDocumentBatch(data: any, maxBytes = DOCUMENT_BATCH_MAX_BYTES): any[] {
  if (!Array.isArray(data) || data.length === 0) {
    return [data]
  }
  const chunks: any[][] = []
  let current: any[] = []
  let currentBytes = 2
  for (const document of data) {
    const documentBytes = jsonUtf8ByteLength(document)
    const separator = current.length === 0 ? 0 : 1
    const nextBytes = currentBytes + separator + documentBytes
    if (current.length > 0 && nextBytes > maxBytes) {
      chunks.push(current)
      current = [document]
      currentBytes = 2 + documentBytes
    } else {
      current.push(document)
      currentBytes = nextBytes
    }
  }
  if (current.length > 0) {
    chunks.push(current)
  }
  return chunks
}
