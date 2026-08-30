import { BezierEdge, BezierEdgeModel, h, type BaseEdgeModel, type GraphModel } from '@logicflow/core'
import type { App } from 'vue'
import { connect, disconnect } from './teleport'
import CustomLine from './CustomLine.vue'

function isMouseInElement(element: Element, event: PointerEvent) {
  const rect = element.getBoundingClientRect()
  return event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom
}
const DEFAULT_WIDTH = 32
const DEFAULT_HEIGHT = 32
class CustomEdge2 extends BezierEdge {
  isMounted = false
  customLineApp?: App<Element>
  root?: HTMLDivElement

  constructor() {
    super()
    this.handleMouseUp = (event?: PointerEvent) => {
      if (!event || !(event.target instanceof Element)) return

      this.props.graphModel.clearSelectElements()
      this.props.model.isSelected = true
      const element = event.target.parentElement?.parentElement?.querySelector('.lf-custom-edge-wrapper')
      if (element && isMouseInElement(element, event)) {
        this.props.model.graphModel.deleteEdgeById(this.props.model.id)
      }
    }
  }
  /**
   * 渲染vue组件
   * @param root
   */
  protected renderVueComponent(root: HTMLDivElement) {
    this.unmountVueComponent()
    this.root = root
    if (root) {
      connect(this.targetId(), CustomLine, root, () => {
        return { getModel: () => this.props.model }
      })
    }
  }
  protected targetId() {
    return `${this.props.graphModel.flowId}:${this.props.model.id}`
  }
  /**
   * 组件即将卸载勾子
   */
  componentWillUnmount() {
    if (super.componentWillUnmount) {
      super.componentWillUnmount()
    }
    disconnect(this.targetId())
    this.unmountVueComponent()
  }
  /**
   * 卸载vue
   * @returns
   */
  protected unmountVueComponent() {
    if (this.customLineApp) {
      this.customLineApp.unmount()
      this.customLineApp = undefined
    }
    if (this.root) {
      this.root.innerHTML = ''
    }
    return this.root
  }

  getEdge() {
    const { model } = this.props
    const id = model.id
    const { customWidth = DEFAULT_WIDTH, customHeight = DEFAULT_HEIGHT } = model.getProperties()
    const { startPoint, endPoint, path, isAnimation, arrowConfig } = model
    const animationStyle = model.getEdgeAnimationStyle()
    const { strokeDasharray, stroke, strokeDashoffset, animationName, animationDuration, animationIterationCount, animationTimingFunction, animationDirection } = animationStyle
    const positionData = { x: (startPoint.x + endPoint.x - customWidth) / 2, y: (startPoint.y + endPoint.y - customHeight) / 2, width: customWidth, height: customHeight }
    const style = model.getEdgeStyle()
    const wrapperStyle = { width: customWidth, height: customHeight }

    setTimeout(() => {
      const s = document.getElementById(id)
      if (s instanceof HTMLDivElement && !this.isMounted) {
        this.isMounted = true
        this.renderVueComponent(s)
      }
    }, 0)

    delete style.stroke

    return h('g', {}, [
      h('style', { type: 'text/css' }, '.lf-edge{stroke:#afafaf}.lf-edge:hover{stroke: #3370FF;}'),
      h('path', {
        d: path,
        ...style,
        ...arrowConfig,
        ...(isAnimation
          ? { strokeDasharray, stroke, style: { strokeDashoffset, animationName, animationDuration, animationIterationCount, animationTimingFunction, animationDirection } }
          : {}),
      }),
      h('foreignObject', { ...positionData, y: positionData.y + 5, x: positionData.x + 5, style: {} }, [
        h('div', { id, style: { ...wrapperStyle }, className: 'lf-custom-edge-wrapper' }),
      ]),
    ])
  }
}

class CustomEdgeModel2 extends BezierEdgeModel {
  getArrowStyle() {
    const arrowStyle = super.getArrowStyle()
    arrowStyle.offset = 1
    arrowStyle.verticalLength = 0
    return arrowStyle
  }

  getEdgeStyle() {
    const style = super.getEdgeStyle()
    // svg属性
    style.strokeWidth = 2
    style.stroke = '#BBBFC4'
    style.offset = 0
    return style
  }
  /**
   * 重写此方法，使保存数据是能带上锚点数据。
   */
  getData() {
    const data = super.getData()
    if (data) {
      data.sourceAnchorId = this.sourceAnchorId
      data.targetAnchorId = this.targetAnchorId
    }
    return data
  }
  /**
   * 给边自定义方案，使其支持基于锚点的位置更新边的路径
   */
  updatePathByAnchor() {
    const sourceNodeModel = this.graphModel.getNodeModelById(this.sourceNodeId)
    const sourceAnchor = sourceNodeModel?.getDefaultAnchor().find((anchor) => anchor.id === this.sourceAnchorId)

    const targetNodeModel = this.graphModel.getNodeModelById(this.targetNodeId)
    const targetAnchor = targetNodeModel?.getDefaultAnchor().find((anchor) => anchor.id === this.targetAnchorId)
    if (sourceAnchor && targetAnchor) {
      const startPoint = { x: sourceAnchor.x, y: sourceAnchor.y }
      this.updateStartPoint(startPoint)
      const endPoint = { x: targetAnchor.x, y: targetAnchor.y }

      this.updateEndPoint(endPoint)
    }

    // 这里需要将原有的pointsList设置为空，才能触发bezier的自动计算control点。
    this.pointsList = []
    this.initPoints()
  }
  setAttributes(): void {
    super.setAttributes()
    this.isHitable = true
    this.zIndex = 0
  }
}

export default { type: 'app-edge', view: CustomEdge2, model: CustomEdgeModel2 }
