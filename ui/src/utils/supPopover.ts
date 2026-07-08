// supPopover.ts
import {
  computePosition,
  flip,
  offset,
  shift,
  arrow,
  autoUpdate,
  type Placement,
} from '@floating-ui/dom'
import DOMPurify from 'dompurify'
let tooltipEl: HTMLDivElement | null = null
let arrowEl: HTMLDivElement | null = null
let contentEl: HTMLDivElement | null = null
let currentSup: HTMLElement | null = null
let cleanupAutoUpdate: (() => void) | null = null
let initialized = false

// ---- 创建 tooltip DOM ----
function createTooltip() {
  const el = document.createElement('div')
  el.className = 'sup-popover'

  const inner = document.createElement('div')
  inner.className = 'sup-popover__content'
  el.appendChild(inner)

  const av = document.createElement('div')
  av.className = 'sup-popover__arrow'
  el.appendChild(av)

  document.body.appendChild(el)
  return { el, arrowEl: av, contentEl: inner }
}

// ---- 定位计算 ----
async function updatePosition(reference: HTMLElement) {
  if (!tooltipEl || !arrowEl) return

  const { x, y, placement, middlewareData } = await computePosition(reference, tooltipEl, {
    placement: 'top',
    middleware: [offset(10), flip(), shift({ padding: 8 }), arrow({ element: arrowEl })],
  })

  Object.assign(tooltipEl.style, { left: `${x}px`, top: `${y}px` })
  tooltipEl.dataset.placement = placement

  const { x: ax, y: ay } = middlewareData.arrow ?? {}
  const side = placement.split('-')[0] as 'top' | 'bottom' | 'left' | 'right'
  const staticSide = { top: 'bottom', bottom: 'top', left: 'right', right: 'left' }[side]

  Object.assign(arrowEl.style, {
    left: '',
    top: '',
    right: '',
    bottom: '',
    ...(ax != null ? { left: `${ax}px` } : {}),
    ...(ay != null ? { top: `${ay}px` } : {}),
    [staticSide]: '-5px',
  })
}

// ---- 显示 / 隐藏 ----
function show(sup: HTMLElement) {
  if (!tooltipEl || !contentEl) return

  // 过滤 XSS，只保留安全的 HTML 标签和属性
  contentEl.innerHTML = DOMPurify.sanitize(sup.dataset.title ?? '')

  tooltipEl.style.display = 'block'
  tooltipEl.style.pointerEvents = 'auto'

  cleanupAutoUpdate?.()
  cleanupAutoUpdate = autoUpdate(sup, tooltipEl, () => updatePosition(sup))
}

function hide() {
  if (!tooltipEl) return
  tooltipEl.style.display = 'none'
  cleanupAutoUpdate?.()
  cleanupAutoUpdate = null
  currentSup = null
}

// ---- 核心：用 pointer 路径判断是否在安全区内 ----
// 记录鼠标坐标
let mouseX = 0
let mouseY = 0
document.addEventListener(
  'mousemove',
  (e) => {
    mouseX = e.clientX
    mouseY = e.clientY
  },
  { passive: true },
)

function isMouseInsideSafeZone(): boolean {
  if (!tooltipEl || !currentSup) return false

  const supRect = currentSup.getBoundingClientRect()
  const tipRect = tooltipEl.getBoundingClientRect()

  // 把 sup 和 tooltip 的 rect 各扩展 2px 容差，
  // 再判断鼠标是否在两个矩形的凸包（union bbox）内
  const pad = 2
  const minX = Math.min(supRect.left, tipRect.left) - pad
  const maxX = Math.max(supRect.right, tipRect.right) + pad
  const minY = Math.min(supRect.top, tipRect.top) - pad
  const maxY = Math.max(supRect.bottom, tipRect.bottom) + pad

  return mouseX >= minX && mouseX <= maxX && mouseY >= minY && mouseY <= maxY
}

// ---- 事件处理 ----
function onMouseOver(e: MouseEvent) {
  const sup = (e.target as HTMLElement).closest('sup[data-title]') as HTMLElement | null
  if (!sup) return

  if (sup !== currentSup) {
    currentSup = sup
    show(sup)
  }
}

function onMouseMove(e: MouseEvent) {
  if (!currentSup) return

  // 鼠标在 tooltip 内部，直接跳过，不做任何处理
  if (tooltipEl && (e.target === tooltipEl || tooltipEl.contains(e.target as Node))) return

  const overSup = (e.target as HTMLElement).closest('sup[data-title]')

  if (!overSup && !isMouseInsideSafeZone()) {
    hide()
  }
}

// ---- 单例公共 API ----
export const supPopover = {
  init() {
    if (initialized) return
    initialized = true

    const els = createTooltip()
    tooltipEl = els.el
    arrowEl = els.arrowEl
    contentEl = els.contentEl

    document.addEventListener('mouseover', onMouseOver)
    document.addEventListener('mousemove', onMouseMove, { passive: true })
  },

  destroy() {
    document.removeEventListener('mouseover', onMouseOver)
    document.removeEventListener('mousemove', onMouseMove)
    cleanupAutoUpdate?.()
    tooltipEl?.remove()
    tooltipEl = null
    arrowEl = null
    contentEl = null
    currentSup = null
    initialized = false
  },
}
