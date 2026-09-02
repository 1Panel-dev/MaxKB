import { BezierEdge, BezierEdgeModel, h } from '@logicflow/core'
import { connect, disconnect } from './teleport'
import DeleteEdgeButton from './DeleteEdgeButton.vue'

const DEFAULT_WIDTH = 24
const DEFAULT_HEIGHT = 24
class CustomEdge2 extends BezierEdge {
  isMounted = false
  root?: HTMLDivElement
  /**
   * 渲染vue组件
   * @param root
   */
  protected renderVueComponent(root: HTMLDivElement) {
    this.unmountVueComponent()
    this.root = root
    if (root) {
      connect(this.targetId(), DeleteEdgeButton, root, () => {
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
    if (this.root) {
      this.root.innerHTML = ''
    }
    return this.root
  }

  getAppendWidth() {
    const { model } = this.props
    const id = model.id
    const { customWidth = DEFAULT_WIDTH, customHeight = DEFAULT_HEIGHT } = model.getProperties()
    const { startPoint, endPoint } = model
    const positionData = {
      x: (startPoint.x + endPoint.x - customWidth) / 2,
      y: (startPoint.y + endPoint.y - customHeight) / 2,
      width: customWidth,
      height: customHeight,
    }

    setTimeout(() => {
      const root = document.getElementById(id)
      if (root instanceof HTMLDivElement && !this.isMounted) {
        this.isMounted = true
        this.renderVueComponent(root)
      }
    }, 0)

    return h('g', {}, [
      super.getAppendWidth(),
      h('foreignObject', { ...positionData, className: 'workflow-edge-delete-wrapper' }, [
        h('div', {
          id,
          className: 'lf-custom-edge-wrapper',
          style: { height: customHeight, width: customWidth },
        }),
      ]),
    ])
  }

  getEdge() {
    const { model } = this.props
    const { path, isAnimation, arrowConfig } = model
    const animationStyle = model.getEdgeAnimationStyle()
    const {
      strokeDasharray,
      stroke,
      strokeDashoffset,
      animationName,
      animationDuration,
      animationIterationCount,
      animationTimingFunction,
      animationDirection,
    } = animationStyle
    const style = model.getEdgeStyle()

    delete style.stroke

    return h('g', {}, [
      h('path', {
        d: path,
        ...style,
        ...arrowConfig,
        ...(isAnimation
          ? {
              strokeDasharray,
              stroke,
              style: { strokeDashoffset, animationName, animationDuration, animationIterationCount, animationTimingFunction, animationDirection },
            }
          : {}),
      }),
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
