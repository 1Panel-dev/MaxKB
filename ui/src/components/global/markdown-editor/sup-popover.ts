/** 管理 Markdown 上标说明的全局悬浮层。 */

import { arrow, autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom'
import DOMPurify from 'dompurify'

let arrowElement: HTMLDivElement | null = null
let contentElement: HTMLDivElement | null = null
let currentSupElement: HTMLElement | null = null
let mouseX = 0
let mouseY = 0
let popoverElement: HTMLDivElement | null = null
let stopAutoUpdate: (() => void) | null = null
let initialized = false

function createPopover() {
  const popover = document.createElement('div')
  popover.className = 'markdown-sup-popover'

  const content = document.createElement('div')
  content.className = 'markdown-sup-popover__content'
  popover.appendChild(content)

  const arrowElement = document.createElement('div')
  arrowElement.className = 'markdown-sup-popover__arrow'
  popover.appendChild(arrowElement)

  document.body.appendChild(popover)
  return { arrowElement, contentElement: content, popoverElement: popover }
}

function updatePosition(referenceElement: HTMLElement) {
  if (!popoverElement || !arrowElement) return

  computePosition(referenceElement, popoverElement, {
    middleware: [offset(10), flip(), shift({ padding: 8 }), arrow({ element: arrowElement })],
    placement: 'top',
  }).then(({ x, y, placement, middlewareData }) => {
    if (!popoverElement || !arrowElement) return

    Object.assign(popoverElement.style, { left: `${x}px`, top: `${y}px` })
    popoverElement.dataset.placement = placement

    const { x: arrowX, y: arrowY } = middlewareData.arrow ?? {}
    const side = placement.split('-')[0] as 'bottom' | 'left' | 'right' | 'top'
    const staticSide = { bottom: 'top', left: 'right', right: 'left', top: 'bottom' }[side]

    Object.assign(arrowElement.style, {
      bottom: '',
      left: arrowX == null ? '' : `${arrowX}px`,
      right: '',
      top: arrowY == null ? '' : `${arrowY}px`,
      [staticSide]: '-5px',
    })
  })
}

function showPopover(supElement: HTMLElement) {
  if (!popoverElement || !contentElement) return

  contentElement.innerHTML = DOMPurify.sanitize(supElement.dataset.title ?? '')
  popoverElement.style.display = 'block'
  popoverElement.style.pointerEvents = 'auto'

  stopAutoUpdate?.()
  stopAutoUpdate = autoUpdate(supElement, popoverElement, () => updatePosition(supElement))
}

function hidePopover() {
  if (!popoverElement) return

  popoverElement.style.display = 'none'
  stopAutoUpdate?.()
  stopAutoUpdate = null
  currentSupElement = null
}

function isMouseInsideSafeZone() {
  if (!popoverElement || !currentSupElement) return false

  const supRect = currentSupElement.getBoundingClientRect()
  const popoverRect = popoverElement.getBoundingClientRect()
  const tolerance = 2
  const minX = Math.min(supRect.left, popoverRect.left) - tolerance
  const maxX = Math.max(supRect.right, popoverRect.right) + tolerance
  const minY = Math.min(supRect.top, popoverRect.top) - tolerance
  const maxY = Math.max(supRect.bottom, popoverRect.bottom) + tolerance

  return mouseX >= minX && mouseX <= maxX && mouseY >= minY && mouseY <= maxY
}

function handleMouseOver(event: MouseEvent) {
  const supElement = (event.target as HTMLElement).closest<HTMLElement>('sup[data-title]')
  if (!supElement || supElement === currentSupElement) return

  currentSupElement = supElement
  showPopover(supElement)
}

function handleMouseMove(event: MouseEvent) {
  mouseX = event.clientX
  mouseY = event.clientY
  if (!currentSupElement) return
  if (popoverElement?.contains(event.target as Node)) return
  if (!(event.target as HTMLElement).closest('sup[data-title]') && !isMouseInsideSafeZone()) hidePopover()
}

export const supPopover = {
  /** 初始化一次全局上标悬浮层与事件监听。 */
  init() {
    if (initialized) return

    const elements = createPopover()
    arrowElement = elements.arrowElement
    contentElement = elements.contentElement
    popoverElement = elements.popoverElement
    document.addEventListener('mousemove', handleMouseMove, { passive: true })
    document.addEventListener('mouseover', handleMouseOver)
    initialized = true
  },

  /** 移除上标悬浮层及其全局事件监听。 */
  destroy() {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseover', handleMouseOver)
    stopAutoUpdate?.()
    popoverElement?.remove()
    arrowElement = null
    contentElement = null
    currentSupElement = null
    popoverElement = null
    stopAutoUpdate = null
    initialized = false
  },
}
