import LogicFlow from '@logicflow/core'
import { shapeList } from './data'
type ShapeItem = {
  type?: string
  text?: string
  icon?: string
  label?: string
  className?: string
  disabled?: boolean
  properties?: Record<string, any>
  callback?: (lf: LogicFlow, container: HTMLElement) => void
}

class AppMenu {
  lf: LogicFlow
  shapeList: ShapeItem[]
  panelEl?: HTMLDivElement
  static pluginName = 'AppMenu'
  domContainer?: HTMLElement
  constructor({ lf }: { lf: LogicFlow }) {
    this.lf = lf
    this.lf.setPatternItems = (shapeList: Array<ShapeItem>) => {
      this.setPatternItems(shapeList)
    }
    this.shapeList = shapeList
    this.panelEl = undefined
    this.domContainer = undefined
  }
  render(lf: LogicFlow, domContainer: HTMLElement) {
    this.destroy()
    if (!this.shapeList || this.shapeList.length === 0) {
      // 首次render后失败后，后续调用setPatternItems支持渲染
      this.domContainer = domContainer
      return
    }
    this.panelEl = document.createElement('div')
    this.panelEl.className = 'lf-dndpanel'
    this.shapeList.forEach((shapeItem) => {
      this.panelEl?.appendChild(this.createDndItem(shapeItem))
    })
    domContainer.appendChild(this.panelEl)
    this.domContainer = domContainer
  }
  destroy() {
    if (this.domContainer && this.panelEl && this.domContainer.contains(this.panelEl)) {
      this.domContainer.removeChild(this.panelEl)
    }
  }
  setPatternItems(shapeList: Array<ShapeItem>) {
    this.shapeList = shapeList
    // 支持渲染后重新设置拖拽面板
    if (this.domContainer) {
      this.render(this.lf, this.domContainer)
    }
  }
  private createDndItem(shapeItem: ShapeItem): HTMLElement {
    const el = document.createElement('div')
    el.className = shapeItem.className ? `lf-dnd-item ${shapeItem.className}` : 'lf-dnd-item'
    const shape = document.createElement('div')
    shape.className = 'lf-dnd-shape'

    if (shapeItem.icon) {
      shape.style.backgroundImage = `url(${shapeItem.icon})`
    }
    el.appendChild(shape)
    if (shapeItem.label) {
      const text = document.createElement('div')
      text.innerText = shapeItem.label
      text.className = 'lf-dnd-text'
      el.appendChild(text)
    }
    if (shapeItem.disabled) {
      el.classList.add('disabled')
      // 保留callback的执行，可用于界面提示当前shapeItem的禁用状态
      el.onmousedown = () => {
        if (shapeItem.callback && this.domContainer) {
          shapeItem.callback(this.lf, this.domContainer)
        }
      }
      return el
    }
    el.onmousedown = () => {
      if (shapeItem.type) {
        this.lf.dnd.startDrag({
          type: shapeItem.type,
          properties: shapeItem.properties
        })
      }
      if (shapeItem.callback && this.domContainer) {
        shapeItem.callback(this.lf, this.domContainer)
      }
    }
    el.ondblclick = (e) => {
      this.lf.graphModel.eventCenter.emit('dnd:panel-dbclick', {
        e,
        data: shapeItem
      })
    }
    el.onclick = (e) => {
      this.lf.graphModel.eventCenter.emit('dnd:panel-click', {
        e,
        data: shapeItem
      })
    }
    el.oncontextmenu = (e) => {
      this.lf.graphModel.eventCenter.emit('dnd:panel-contextmenu', {
        e,
        data: shapeItem
      })
    }
    return el
  }
}

export { AppMenu }
