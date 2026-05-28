export type CompareOptions =
  | 'eq'
  | 'not_eq'
  | 'contain'
  | 'not_contain'
  | 'is_true'
  | 'is_not_true'
  | 'gt'
  | 'ge'
  | 'lt'
  | 'le'

export interface VisibilityCondition {
  id: string
  field: [string, string] // [scope_or_node_id, field_name]
  compare: CompareOptions | ''
  value: any
  _left?: any // cross node exist
}

export interface VisibilityRules {
  action: 'show' | 'hide'
  condition: 'and' | 'or'
  node_id?: string
  node_name?: string
  conditions: VisibilityCondition[]
}

export interface VisibilityCtx {
  formValue: Record<string, any>
  currentNodeId: string // field 同节点判读 node_id
  currentNodeName: string // current node display name, {{currentNodeName.result}}, same form value. reference
}

/**
 * 解析 匹配值 残留的 {{}}
 *
 * 前端只处理 同 node 表单 引用
 * ex: 当前节点叫「表单收集」，{{表单收集.region}} → formValue.region
 *
 * 跨节点 {{开始.question}} / {{全局变量.x}} / {{chat.x}} 已由后端 form-node
 * reset_field 阶段（过滤掉本节点的 field_list 后）通过 generate_prompt
 * 预渲染为字面量，前端不会再看到这些形态。
 */
export function resolveValue(raw: string, ctx: VisibilityCtx): string {
  return raw.replace(/\{\{([^.\s}]+)\.([^.\s}]+)\}\}/g, (match, nodeName, fieldName) => {
    if (nodeName !== ctx.currentNodeName) {
      return match // 非同表单，前置node 引用
    }
    const v = ctx.formValue?.[fieldName]
    return v == null ? match : String(v)
  })
}

export function lookupLeft(cond: VisibilityCondition, ctx: VisibilityCtx): any {
  const scope = cond.field[0] === 'global' ? 'base-node' : cond.field[0]
  if (scope === ctx.currentNodeId) {
    return ctx.formValue?.[cond.field[1]] // 同节点：实时从 formValue 取
  }
  return (cond as any)._left // 跨节点：后端 返回
}

type CmpFn = (left: any, right: any) => boolean

const compareHandlers: Record<CompareOptions, CmpFn> = {
  eq: (l, r) => String(l) === String(r),
  not_eq: (l, r) => String(l) !== String(r),
  contain: (l, r) => containImpl(l, r),
  not_contain: (l, r) => !containImpl(l, r),
  is_true: (l) => l === true,
  is_not_true: (l) => l !== true,
  gt: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a > b,
      (a, b) => a > b,
    ),
  ge: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a >= b,
      (a, b) => a >= b,
    ),
  lt: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a < b,
      (a, b) => a < b,
    ),
  le: (l, r) =>
    numOrStrCmp(
      l,
      r,
      (a, b) => a <= b,
      (a, b) => a <= b,
    ),
}

export function compareByOp(left: any, op: CompareOptions, right: any): boolean {
  const fn = compareHandlers[op]
  if (!fn) throw new Error(`Unknown compare op: ${op}`)
  return fn(left, right)
}

function containImpl(source: any, target: any): boolean {
  if (Array.isArray(target)) {
    return target.every((t) => containImpl(source, t))
  }
  const t = String(target)
  if (typeof source === 'string') return source.includes(t)
  if (Array.isArray(source)) return source.some((item) => String(item) === t)
  return String(source).includes(t)
}

function numOrStrCmp(
  left: any,
  right: any,
  numFn: (a: number, b: number) => boolean,
  strFn: (a: string, b: string) => boolean,
): boolean {
  const a = Number(left)
  const b = Number(right)
  if (!Number.isNaN(a) && !Number.isNaN(b)) return numFn(a, b)
  try {
    return strFn(String(left), String(right))
  } catch {
    return false
  }
}

export function evaluateVisibility(
  rules: VisibilityRules | null | undefined,
  ctx: VisibilityCtx,
): boolean {
  if (!rules || !rules.conditions || rules.conditions.length === 0) {
    return true
  }

  const results = rules.conditions.map((cond) => {
    const left = lookupLeft(cond, ctx)

    if (left == null && cond.compare !== 'is_true' && cond.compare !== 'is_not_true') {
      return false
    }

    const right = typeof cond.value === 'string' ? resolveValue(cond.value, ctx) : cond.value
    return compareByOp(left, cond.compare as CompareOptions, right)
  })

  const matched = rules.condition === 'or' ? results.some(Boolean) : results.every(Boolean)

  return rules.action === 'show' ? matched : !matched
}

/**
 * 单向扫描计算整个字段列表的显隐表。
 * @param fields
 * @param formValue
 * @returns { 字段名: 是否可见 } 的 map
 */
export function computeVisibilityMap(
  fields: Array<{ field: string; visibility_rules?: VisibilityRules }>,
  formValue: Record<string, any>,
): Record<string, boolean> {
  const copy: Record<string, any> = { ...formValue }
  const map: Record<string, boolean> = {}

  for (const f of fields) {
    if (!f.visibility_rules?.node_id) {
      map[f.field] = true
      continue
    }

    const visible = evaluateVisibility(f.visibility_rules, {
      formValue: copy,
      currentNodeId: f.visibility_rules.node_id,
      currentNodeName: f.visibility_rules.node_name || '',
    })
    map[f.field] = visible
    if (!visible) {
      copy[f.field] = null
    }
  }
  return map
}
