import Components from '@/components'
import ElementPlus from 'element-plus'
import { HtmlNode, HtmlNodeModel } from '@logicflow/core'
import { createApp, h } from 'vue'
import directives from '@/directives'

class AppNode extends HtmlNode {
  isMounted
  r
  app

  constructor(props: any, VueNode: any) {
    super(props)
    this.isMounted = false

    this.r = h(VueNode, {
      properties: props.model.properties,
      nodeModel: props.model
    })

    this.app = createApp({
      render: () => this.r
    })
    this.app.use(ElementPlus)
    this.app.use(Components)
    this.app.use(directives)
  }

  setHtml(rootEl: HTMLElement) {
    if (!this.isMounted) {
      this.isMounted = true
      const node = document.createElement('div')
      rootEl.appendChild(node)
      this.app.mount(node)
    } else {
      if (this.r && this.r.component) {
        this.r.component.props.properties = this.props.model.getProperties()
      }
    }
  }
}

class AppNodeModel extends HtmlNodeModel {
  /**
   * 给model自定义添加字段方法
   */
  addField(item: any) {
    this.properties.fields.unshift(item)
    this.setAttributes()
    // 为了保持节点顶部位置不变，在节点变化后，对节点进行一个位移,位移距离为添加高度的一半。
    this.move(0, 24 / 2)
    // 更新节点连接边的path
    this.incoming.edges.forEach((egde: any) => {
      // 调用自定义的更新方案
      egde.updatePathByAnchor()
    })
    this.outgoing.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
  }
  getOutlineStyle() {
    const style = super.getOutlineStyle()
    style.stroke = 'none'
    if (style.hover) {
      style.hover.stroke = 'none'
    }
    return style
  }
  // 如果不用修改锚地形状，可以重写颜色相关样式
  getAnchorStyle(anchorInfo: any) {
    const style = super.getAnchorStyle(anchorInfo)
    if (anchorInfo.type === 'left') {
      style.fill = 'red'
      style.hover.fill = 'transparent'
      style.hover.stroke = 'transpanrent'
      style.className = 'lf-hide-default'
    } else {
      style.fill = 'green'
    }
    return style
  }
  setHeight(height: number, inputContainerHeight: number, outputContainerHeight: number) {
    this.height = height + inputContainerHeight + outputContainerHeight + 100
    this.baseHeight = height
    this.inputContainerHeight = inputContainerHeight
    this.outputContainerHeight = outputContainerHeight

    this.outgoing.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
    this.incoming.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
  }
  setAttributes() {
    this.width = 500

    const circleOnlyAsTarget = {
      message: '只允许从右边的锚点连出',
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any) => {
        return sourceAnchor.type === 'right'
      }
    }
    this.sourceRules.push(circleOnlyAsTarget)
    this.targetRules.push({
      message: '只允许连接左边的锚点',
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
        return targetAnchor.type === 'left'
      }
    })
  }
  getDefaultAnchor() {
    const {
      id,
      x,
      y,
      width,
      height,
      properties: { input, output }
    } = this

    if (this.baseHeight === undefined) {
      this.baseHeight = 0
    }
    if (this.inputContainerHeight === undefined) {
      this.inputContainerHeight = 0
    }
    if (this.height === undefined) {
      this.height = 200
    }
    if (this.outputContainerHeight === undefined) {
      this.outputContainerHeight = 0
    }

    const anchors: any = []
    if (input) {
      input.forEach((field: any, index: any) => {
        anchors.push({
          x: x - width / 2 + 10,
          y: y - height / 2 + this.baseHeight + 35 + index * 24,
          id: `${id}_${field.key}_left`,
          edgeAddable: false,
          type: 'left'
        })
      })
    }
    if (output) {
      output.forEach((field: any, index: any) => {
        anchors.push({
          x: x + width / 2 - 10,
          y: y - height / 2 + this.baseHeight + this.inputContainerHeight + 30 + index * 24,
          id: `${id}_${field.key}_right`,
          type: 'right'
        })
      })
    }

    return anchors
  }
}

export { AppNodeModel, AppNode }
