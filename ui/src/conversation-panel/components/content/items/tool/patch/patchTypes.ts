export type PatchFileStatus = 'add' | 'modify' | 'delete' | 'rename' | 'copy' | 'mode' | 'binary' | 'unknown'

export type PatchLineType = 'add' | 'remove' | 'context' | 'hunk' | 'meta' | 'empty'

export interface PatchLine {
  type: PatchLineType
  oldLineNumber: number | null
  newLineNumber: number | null
  displayLineNumber: number | null
  prefix: string
  content: string
  raw: string
}

export interface PatchFileInfo {
  status: PatchFileStatus
  oldPath: string
  newPath: string
  additions: number
  deletions: number
  isBinary: boolean
  lines: PatchLine[]
}
