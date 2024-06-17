import Components from '@/components'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import { HtmlNode, HtmlNodeModel, BaseEdge } from '@logicflow/core'
import { createApp, h } from 'vue'
import directives from '@/directives'
import i18n from '@/locales'

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
    this.app.use(i18n)
    for (const [key, component] of Object.entries(ElementPlusIcons)) {
      this.app.component(key, component)
    }

    if (props.model.properties.noRender) {
      delete props.model.properties.noRender
    } else {
      const filterNodes = props.graphModel.nodes.filter((v: any) => v.type === props.model.type)
      if (filterNodes.length - 1 > 0) {
        props.model.properties.stepName = props.model.properties.stepName + (filterNodes.length - 1)
      }
    }
    if (props.model.properties?.fields?.length > 0) {
      props.model.properties.fields.map((item: any) => {
        item['globeLabel'] = `{{${props.model.properties.stepName}.${item.value}}}`
        item['globeValue'] = `{{context['${props.model.id}'].${item.value}}}`
      })
    }
  }

  setHtml(rootEl: HTMLElement) {
    if (!this.isMounted) {
      this.isMounted = true
      const node = document.createElement('div')
      rootEl.appendChild(node)
      this.app?.mount(node)
    } else {
      if (this.r && this.r.component) {
        this.r.component.props.properties = this.props.model.getProperties()
      }
    }
  }
}

class AppNodeModel extends HtmlNodeModel {
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

  setHeight(height: number) {
    this.height = height + 100
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
    this.width = this.properties?.width || 340
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
    const { id, x, y, width } = this
    const anchors: any = []
    if (this.type !== 'start-node') {
      anchors.push({
        x: x - width / 2 + 10,
        y: y,
        id: `${id}_left`,
        edgeAddable: false,
        type: 'left'
      })
    }

    anchors.push({
      x: x + width / 2 - 10,
      y: y,
      id: `${id}_right`,
      type: 'right'
    })

    return anchors
  }
}

export { AppNodeModel, AppNode }
