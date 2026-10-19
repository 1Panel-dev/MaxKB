import type { PatchFileInfo, PatchFileStatus, PatchLine } from './patchTypes'

function normalizePath(path: string) {
  if (!path || path === '/dev/null') {
    return ''
  }

  return path.replace(/^a\//, '').replace(/^b\//, '').replace(/^"a\//, '"').replace(/^"b\//, '"').replace(/^"|"$/g, '')
}

function parseDiffGitLine(line: string) {
  const match = line.match(/^diff --git\s+(.+)\s+(.+)$/)

  if (!match) {
    return {
      oldPath: '',
      newPath: '',
    }
  }

  return {
    oldPath: normalizePath(match[1] ?? ''),
    newPath: normalizePath(match[2] ?? ''),
  }
}

function detectStatus(lines: string[]): PatchFileStatus {
  if (lines.some((line) => line.startsWith('Binary files '))) {
    return 'binary'
  }

  if (lines.some((line) => line.startsWith('rename from '))) {
    return 'rename'
  }

  if (lines.some((line) => line.startsWith('copy from '))) {
    return 'copy'
  }

  if (lines.some((line) => line.startsWith('new file mode'))) {
    return 'add'
  }

  if (lines.some((line) => line.startsWith('deleted file mode'))) {
    return 'delete'
  }

  if (lines.some((line) => line.startsWith('old mode ')) || lines.some((line) => line.startsWith('new mode '))) {
    return 'mode'
  }

  if (lines.some((line) => line.startsWith('@@'))) {
    return 'modify'
  }

  return 'unknown'
}

function getValueAfterPrefix(lines: string[], prefix: string) {
  const line = lines.find((item) => item.startsWith(prefix))

  if (!line) {
    return ''
  }

  return line.slice(prefix.length).trim()
}

function parseHunkStart(line: string) {
  const match = line.match(/^@@\s+-(\d+)(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@/)

  if (!match) {
    return null
  }

  return {
    oldLine: Number(match[1]),
    newLine: Number(match[2]),
  }
}

function createMetaLine(raw: string): PatchLine {
  return {
    type: 'meta',
    oldLineNumber: null,
    newLineNumber: null,
    displayLineNumber: null,
    prefix: '',
    content: raw,
    raw,
  }
}

function parseLines(lines: string[]) {
  const result: PatchLine[] = []

  let oldLine = 0
  let newLine = 0
  let inHunk = false

  for (const raw of lines) {
    if (raw.startsWith('diff --git ')) {
      continue
    }

    if (raw.startsWith('@@')) {
      const hunkStart = parseHunkStart(raw)

      if (hunkStart) {
        oldLine = hunkStart.oldLine
        newLine = hunkStart.newLine
        inHunk = true
      }

      result.push({
        type: 'hunk',
        oldLineNumber: null,
        newLineNumber: null,
        displayLineNumber: null,
        prefix: '',
        content: raw,
        raw,
      })
      continue
    }

    if (!inHunk) {
      if (
        raw.startsWith('new file mode') ||
        raw.startsWith('deleted file mode') ||
        raw.startsWith('similarity index') ||
        raw.startsWith('dissimilarity index') ||
        raw.startsWith('rename from') ||
        raw.startsWith('rename to') ||
        raw.startsWith('copy from') ||
        raw.startsWith('copy to') ||
        raw.startsWith('old mode') ||
        raw.startsWith('new mode') ||
        raw.startsWith('index ') ||
        raw.startsWith('--- ') ||
        raw.startsWith('+++ ') ||
        raw.startsWith('Binary files ')
      ) {
        result.push(createMetaLine(raw))
      }

      continue
    }

    if (raw.startsWith('+') && !raw.startsWith('+++')) {
      result.push({
        type: 'add',
        oldLineNumber: null,
        newLineNumber: newLine,
        displayLineNumber: newLine,
        prefix: '+',
        content: raw.slice(1),
        raw,
      })
      newLine += 1
      continue
    }

    if (raw.startsWith('-') && !raw.startsWith('---')) {
      result.push({
        type: 'remove',
        oldLineNumber: oldLine,
        newLineNumber: null,
        displayLineNumber: oldLine,
        prefix: '-',
        content: raw.slice(1),
        raw,
      })
      oldLine += 1
      continue
    }

    if (raw.startsWith(' ')) {
      result.push({
        type: 'context',
        oldLineNumber: oldLine,
        newLineNumber: newLine,
        displayLineNumber: newLine,
        prefix: '',
        content: raw.slice(1),
        raw,
      })
      oldLine += 1
      newLine += 1
      continue
    }

    if (raw === '\\ No newline at end of file') {
      result.push(createMetaLine(raw))
      continue
    }

    result.push({
      type: 'empty',
      oldLineNumber: oldLine,
      newLineNumber: newLine,
      displayLineNumber: newLine,
      prefix: '',
      content: raw,
      raw,
    })

    oldLine += 1
    newLine += 1
  }

  return result
}

function countChanges(lines: PatchLine[]) {
  let additions = 0
  let deletions = 0

  for (const line of lines) {
    if (line.type === 'add') {
      additions += 1
    }

    if (line.type === 'remove') {
      deletions += 1
    }
  }

  return {
    additions,
    deletions,
  }
}

export function parsePatch(diff: string): PatchFileInfo[] {
  const blocks = diff
    .replace(/\r\n/g, '\n')
    .split(/\n(?=diff --git )/)
    .map((block) => block.trimEnd())
    .filter(Boolean)

  return blocks.map((block) => {
    const rawLines = block.split('\n')
    const firstLine = rawLines[0] ?? ''
    const parsedPath = parseDiffGitLine(firstLine)
    const status = detectStatus(rawLines)
    const lines = parseLines(rawLines)
    const changes = countChanges(lines)

    let oldPath = parsedPath.oldPath
    let newPath = parsedPath.newPath

    if (status === 'rename') {
      oldPath = getValueAfterPrefix(rawLines, 'rename from ') || oldPath
      newPath = getValueAfterPrefix(rawLines, 'rename to ') || newPath
    }

    if (status === 'copy') {
      oldPath = getValueAfterPrefix(rawLines, 'copy from ') || oldPath
      newPath = getValueAfterPrefix(rawLines, 'copy to ') || newPath
    }

    if (status === 'add') {
      oldPath = ''
    }

    if (status === 'delete') {
      newPath = ''
    }

    return {
      status,
      oldPath,
      newPath,
      additions: changes.additions,
      deletions: changes.deletions,
      isBinary: status === 'binary',
      lines,
    }
  })
}
