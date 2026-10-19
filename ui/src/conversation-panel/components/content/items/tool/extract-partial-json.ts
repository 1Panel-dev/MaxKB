/**
 * 工业级不完整 JSON 字符串字段提取器
 *
 * 适用场景：流式累加的 JSON 快照（如 LLM tool_call.arguments 的增量拼接）。
 *
 * 性能设计：
 *   1. 快速路径判断——仅在 JSON 可能完整时才调 JSON.parse，避免无谓异常
 *   2. 单次 O(n) 扫描，零中间对象分配（无 readEscape 返回对象）
 *   3. charCodeAt 替代字符串比较，减少临时字符串
 *   4. 大值字段用 chunks[] + join，避免 O(n²) 拼接
 *   5. 纯函数，无状态，无副作用
 *
 * 限制：只提取顶层字符串字段，嵌套对象/数组内的同名字段会被跳过。
 */

// ── 公共类型 ────────────────────────────────────────────────────────────────

/** 提取结果：字段名 → 已还原转义的字符串值 */
export type PartialJsonFields = Record<string, string>

// ── 公共 API ────────────────────────────────────────────────────────────────

/**
 * 从（可能不完整的）JSON 字符串中提取指定的顶层字符串字段。
 *
 * @param raw    JSON 字符串，允许被截断在任意位置
 * @param fields 要提取的字段名；不传或空数组 = 提取所有顶层字符串字段
 * @returns      字段名 → 值。未出现/无法提取的字段不在结果中
 *
 * @example
 *   extractPartialJsonFields('{"patch":"diff --git a/f','  ['patch'])
 *   // => { patch: 'diff --git a/f' }
 */
export function extractPartialJsonFields(raw: string | null | undefined, fields?: Iterable<string>): PartialJsonFields {
  if (!raw) return EMPTY

  const wanted = fields ? new Set(fields) : null
  const wantAll = !wanted || wanted.size === 0

  // ── 快速路径：仅当 JSON "看起来完整" 时才尝试 JSON.parse ──
  // 避免在流式中途每次都抛异常（异常创建含堆栈捕获，开销远大于普通分支）
  if (looksComplete(raw)) {
    try {
      const obj = JSON.parse(raw)
      if (obj !== null && typeof obj === 'object' && !Array.isArray(obj)) {
        const out: PartialJsonFields = {}
        const keys = Object.keys(obj)
        for (let i = 0; i < keys.length; i++) {
          const k = keys[i]!
          const v = obj[k]
          if (typeof v === 'string' && (wantAll || wanted!.has(k))) {
            out[k] = v
          }
        }
        return out
      }
      return EMPTY
    } catch {
      // 极少数情况：看起来完整但实际无效，fallthrough 到扫描
    }
  }

  // ── 宽松扫描路径 ──
  return scanPartial(raw, wanted, wantAll)
}

/**
 * 便捷版：只取一个字段，直接返回字符串。
 *
 * @example
 *   extractPartialJsonField('{"patch":"diff --git', 'patch')  // => 'diff --git'
 *   extractPartialJsonField('garbage', 'patch')               // => ''
 */
export function extractPartialJsonField(raw: string | null | undefined, field: string): string {
  return extractPartialJsonFields(raw, [field])[field] ?? ''
}

// ── 内部常量 ─────────────────────────────────────────────────────────────────

const EMPTY: PartialJsonFields = Object.freeze(Object.create(null))

// charCode 常量，避免反复调用 charCodeAt 或字符串比较
const CC_TAB = 0x09 // \t
const CC_LF = 0x0a // \n
const CC_CR = 0x0d // \r
const CC_SPACE = 0x20 // ' '
const CC_DQUOTE = 0x22 // "
const CC_COLON = 0x3a // :
const CC_BACKSLASH = 0x5c // \
const CC_LBRACE = 0x7b // {
const CC_RBRACE = 0x7d // }
const CC_LBRACKET = 0x5b // [
const CC_RBRACKET = 0x5d // ]

const CC_b = 0x62
const CC_f = 0x66
const CC_n = 0x6e
const CC_r = 0x72
const CC_t = 0x74
const CC_u = 0x75
const CC_SLASH = 0x2f // /

// ── 内部函数 ─────────────────────────────────────────────────────────────────

/**
 * 快速判断 raw 是否"看起来像完整的 JSON 对象"。
 * 不做完整语法校验——只检查 trim 后是否以 { 开头、以 } 结尾。
 * 误判率极低，代价极小。
 */
function looksComplete(raw: string): boolean {
  const len = raw.length
  // 从头找第一个非空白字符
  let start = 0
  while (start < len) {
    const c = raw.charCodeAt(start)
    if (c !== CC_SPACE && c !== CC_TAB && c !== CC_LF && c !== CC_CR) break
    start++
  }
  // 从尾找最后一个非空白字符
  let end = len - 1
  while (end > start) {
    const c = raw.charCodeAt(end)
    if (c !== CC_SPACE && c !== CC_TAB && c !== CC_LF && c !== CC_CR) break
    end--
  }
  return start < len && raw.charCodeAt(start) === CC_LBRACE && raw.charCodeAt(end) === CC_RBRACE
}

/** 扫描器状态 */
const enum State {
  /** 在顶层对象内，等待 key 或结构字符 */
  TOP = 0,
  /** 正在读 key 的字符串内容 */
  KEY = 1,
  /** key 读完，等冒号 */
  COLON = 2,
  /** 冒号读完，等 value 起始 */
  VALUE = 3,
  /** 正在跳过一个不需要的字符串值 */
  SKIP_STR = 4,
  /** 正在读取一个需要的字符串值 */
  TAKE_STR = 5,
}

/**
 * 单次扫描整个快照，提取顶层字符串字段。
 *
 * 核心优化：
 *   - charCodeAt 代替 raw[i] 字符串比较
 *   - 转义处理内联（无函数调用、无对象分配）
 *   - 大值用 chunks 数组收集，最后 join
 */
function scanPartial(raw: string, wanted: Set<string> | null, wantAll: boolean): PartialJsonFields {
  const out: PartialJsonFields = Object.create(null)
  const len = raw.length

  let state: State = State.TOP
  let objectDepth = 0
  let arrayDepth = 0

  // key 累积（key 通常很短，直接拼接）
  let key = ''

  // 当前正在收集的字段
  let curField = ''
  // 值累积：用 chunks + tail 模式
  // tail 收集当前连续的非转义字符；遇到转义或结束时 push 到 chunks
  let chunks: string[] = []
  let tailStart = 0 // raw 中连续片段的起始索引
  let tailHasContent = false

  /** 将 tailStart..i 的片段和 chunks 合并为最终字符串 */
  const flushValue = (endIndex: number): string => {
    if (tailHasContent) {
      chunks.push(raw.slice(tailStart, endIndex))
    }
    if (chunks.length === 0) return ''
    if (chunks.length === 1) return chunks[0]!
    return chunks.join('')
  }

  /** 重置值收集状态 */
  const resetValue = () => {
    chunks = []
    tailStart = 0
    tailHasContent = false
  }

  for (let i = 0; i < len; i++) {
    const cc = raw.charCodeAt(i)

    switch (state) {
      case State.TOP: {
        if (cc === CC_LBRACE) {
          objectDepth++
        } else if (cc === CC_RBRACE) {
          if (objectDepth > 0) objectDepth--
        } else if (cc === CC_LBRACKET) {
          arrayDepth++
        } else if (cc === CC_RBRACKET) {
          if (arrayDepth > 0) arrayDepth--
        } else if (cc === CC_DQUOTE) {
          if (objectDepth === 1 && arrayDepth === 0) {
            state = State.KEY
            key = ''
          } else {
            // 嵌套层字符串，整体跳过
            state = State.SKIP_STR
          }
        }
        break
      }

      case State.KEY: {
        if (cc === CC_BACKSLASH) {
          // key 中的转义——内联处理，不分配对象
          i++
          if (i >= len) break // 截断
          key += resolveEscapeChar(raw, i)
          // \uXXXX 需要额外跳过
          if (raw.charCodeAt(i) === CC_u) {
            const hex = raw.slice(i + 1, i + 5)
            if (hex.length === 4 && isHex4(hex)) {
              key += String.fromCharCode(parseInt(hex, 16))
              i += 4
            }
            // 不足 4 位——key 被截断，循环自然结束
          }
        } else if (cc === CC_DQUOTE) {
          state = State.COLON
        } else {
          key += raw[i]
        }
        break
      }

      case State.COLON: {
        if (cc === CC_SPACE || cc === CC_TAB || cc === CC_LF || cc === CC_CR) break
        if (cc === CC_COLON) {
          state = State.VALUE
        } else {
          state = State.TOP
        }
        break
      }

      case State.VALUE: {
        if (cc === CC_SPACE || cc === CC_TAB || cc === CC_LF || cc === CC_CR) break
        if (cc === CC_DQUOTE) {
          if (wantAll || (wanted !== null && wanted.has(key))) {
            state = State.TAKE_STR
            curField = key
            resetValue()
            tailStart = i + 1
            tailHasContent = true
          } else {
            state = State.SKIP_STR
          }
        } else {
          // 非字符串值
          if (cc === CC_LBRACE) objectDepth++
          else if (cc === CC_LBRACKET) arrayDepth++
          state = State.TOP
        }
        break
      }

      case State.SKIP_STR: {
        if (cc === CC_BACKSLASH) {
          i++ // 跳过转义的下一个字符
        } else if (cc === CC_DQUOTE) {
          state = State.TOP
        }
        break
      }

      case State.TAKE_STR: {
        if (cc === CC_BACKSLASH) {
          // 先 flush 反斜杠之前的连续片段
          if (tailHasContent) {
            chunks.push(raw.slice(tailStart, i))
            tailHasContent = false
          }

          i++
          if (i >= len) break // 反斜杠在末尾，截断

          const esc = raw.charCodeAt(i)
          if (esc === CC_u) {
            const hex = raw.slice(i + 1, i + 5)
            if (hex.length === 4 && isHex4(hex)) {
              chunks.push(String.fromCharCode(parseInt(hex, 16)))
              i += 4
            } else {
              // \uXXXX 被截断——丢弃，结束扫描
              break
            }
          } else {
            chunks.push(ESCAPE_MAP[esc] ?? raw[i] ?? '')
          }

          // 下一段连续片段从 i+1 开始
          tailStart = i + 1
          tailHasContent = true
        } else if (cc === CC_DQUOTE) {
          // 值正常闭合
          const val = flushValue(i)
          out[curField] = curField in out ? out[curField] + val : val
          curField = ''
          state = State.TOP
        }
        // 普通字符：tail 自然延伸，不做任何操作（零开销）
        break
      }
    }
  }

  // 扫描结束时仍在 TAKE_STR——值被截断，收集已有部分
  if (state === State.TAKE_STR && curField) {
    const val = flushValue(len)
    out[curField] = curField in out ? out[curField] + val : val
  }

  return out
}

// ── 转义辅助 ─────────────────────────────────────────────────────────────────

/**
 * 转义字符查找表（用 charCode 索引）。
 * 只覆盖 JSON 标准转义字符；其余 fallback 到原字符（容错）。
 */
const ESCAPE_MAP: Record<number, string> = {
  [CC_n]: '\n',
  [CC_t]: '\t',
  [CC_r]: '\r',
  [CC_b]: '\b',
  [CC_f]: '\f',
  [CC_DQUOTE]: '"',
  [CC_BACKSLASH]: '\\',
  [CC_SLASH]: '/',
}

/**
 * KEY 阶段的简单转义解析（非 \u 部分）。
 * key 很短，这里用字符串返回可以接受。
 */
function resolveEscapeChar(raw: string, i: number): string {
  const cc = raw.charCodeAt(i)
  if (cc === CC_u) return '' // 由调用方单独处理 \uXXXX
  return ESCAPE_MAP[cc] ?? raw[i] ?? ''
}

/** 判断 4 个字符是否全是十六进制 */
function isHex4(s: string): boolean {
  for (let i = 0; i < 4; i++) {
    const c = s.charCodeAt(i)
    if (
      !(c >= 0x30 && c <= 0x39) && // 0-9
      !(c >= 0x41 && c <= 0x46) && // A-F
      !(c >= 0x61 && c <= 0x66) // a-f
    ) {
      return false
    }
  }
  return true
}
