import Components from '@/components'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'

import { HtmlResize } from '@logicflow/extension'

import { h as lh } from '@logicflow/core'
import { createApp, h } from 'vue'
import directives from '@/directives'
import i18n from '@/locales'
import { WorkflowType } from '@/enums/workflow'
import { nodeDict } from '@/workflow/common/data'
class AppNode extends HtmlResize.view {
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
    props.model.properties.config = nodeDict[props.model.type].properties.config
    if (props.model.properties.height) {
      props.model.height = props.model.properties.height
    }
  }

  getAnchorShape(anchorData: any) {
    const { x, y, type } = anchorData
    let isConnect = false

    if (type == 'left') {
      isConnect = this.props.graphModel.edges.some((edge) => edge.targetAnchorId == anchorData.id)
    } else {
      isConnect = this.props.graphModel.edges.some((edge) => edge.sourceAnchorId == anchorData.id)
    }

    return lh(
      'foreignObject',
      {
        ...anchorData,
        x: x - 10,
        y: y - 12,
        width: 30,
        height: 30
      },
      [
        lh('div', {
          dangerouslySetInnerHTML: {
            __html: isConnect
              ? `<svg width="100%" height="100%" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
              <g filter="url(#filter0_d_5119_232585)">
              <path d="M20.9998 29.8333C28.0875 29.8333 33.8332 24.0876 33.8332 17C33.8332 9.91231 28.0875 4.16663 20.9998 4.16663C13.9122 4.16663 8.1665 9.91231 8.1665 17C8.1665 24.0876 13.9122 29.8333 20.9998 29.8333Z" fill="white"/>
              <path fill-rule="evenodd" clip-rule="evenodd" d="M20.9998 27.5C26.7988 27.5 31.4998 22.799 31.4998 17C31.4998 11.201 26.7988 6.49996 20.9998 6.49996C15.2008 6.49996 10.4998 11.201 10.4998 17C10.4998 22.799 15.2008 27.5 20.9998 27.5ZM33.8332 17C33.8332 24.0876 28.0875 29.8333 20.9998 29.8333C13.9122 29.8333 8.1665 24.0876 8.1665 17C8.1665 9.91231 13.9122 4.16663 20.9998 4.16663C28.0875 4.16663 33.8332 9.91231 33.8332 17Z" fill="#3370FF"/>
              </g>
              <defs>
              <filter id="filter0_d_5119_232585" x="-1" y="-1" width="44" height="44" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
              <feFlood flood-opacity="0" result="BackgroundImageFix"/>
              <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
              <feOffset dy="4"/>
              <feGaussianBlur stdDeviation="4"/>
              <feComposite in2="hardAlpha" operator="out"/>
              <feColorMatrix type="matrix" values="0 0 0 0 0.2 0 0 0 0 0.439216 0 0 0 0 1 0 0 0 0.1 0"/>
              <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_5119_232585"/>
              <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_5119_232585" result="shape"/>
              </filter>
              </defs>
              </svg>
              `
              : `<svg width="100%" height="100%" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g filter="url(#filter0_d_5199_166905)">
        <path d="M20.9998 29.8333C28.0875 29.8333 33.8332 24.0876 33.8332 17C33.8332 9.91231 28.0875 4.16663 20.9998 4.16663C13.9122 4.16663 8.1665 9.91231 8.1665 17C8.1665 24.0876 13.9122 29.8333 20.9998 29.8333Z" fill="#3370FF"/>
        <path d="M19.8332 11.75C19.8332 11.4278 20.0943 11.1666 20.4165 11.1666H21.5832C21.9053 11.1666 22.1665 11.4278 22.1665 11.75V15.8333H26.2498C26.572 15.8333 26.8332 16.0945 26.8332 16.4166V17.5833C26.8332 17.9055 26.572 18.1666 26.2498 18.1666H22.1665V22.25C22.1665 22.5721 21.9053 22.8333 21.5832 22.8333H20.4165C20.0943 22.8333 19.8332 22.5721 19.8332 22.25V18.1666H15.7498C15.4277 18.1666 15.1665 17.9055 15.1665 17.5833V16.4166C15.1665 16.0945 15.4277 15.8333 15.7498 15.8333H19.8332V11.75Z" fill="white"/>
        </g>
        <defs>
        <filter id="filter0_d_5199_166905" x="-1" y="-1" width="44" height="44" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
        <feFlood flood-opacity="0" result="BackgroundImageFix"/>
        <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
        <feOffset dy="4"/>
        <feGaussianBlur stdDeviation="4"/>
        <feComposite in2="hardAlpha" operator="out"/>
        <feColorMatrix type="matrix" values="0 0 0 0 0.2 0 0 0 0 0.439216 0 0 0 0 1 0 0 0 0.1 0"/>
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_5199_166905"/>
        <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_5199_166905" result="shape"/>
        </filter>
        </defs>
        </svg>`
          }
        })
      ]
    )
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

class AppNodeModel extends HtmlResize.model {
  getResizeOutlineStyle() {
    const style = super.getResizeOutlineStyle()
    style.stroke = 'none'
    return style
  }
  getControlPointStyle() {
    const style = super.getControlPointStyle()
    style.stroke = 'none'
    style.fill = 'none'
    return style
  }
  getNodeStyle() {
    return {
      overflow: 'visible'
    }
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

  setHeight(height: number) {
    const sourceHeight = this.height
    const targetHeight = height + 100
    this.height = targetHeight
    this.properties['height'] = targetHeight
    this.move(0, (targetHeight - sourceHeight) / 2)
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

    this.sourceRules.push({
      message: '只允许连一个节点',
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
        return !this.graphModel.edges.some(
          (item) =>
            item.sourceAnchorId === sourceAnchor.id || item.targetAnchorId === targetAnchor.id
        )
      }
    })

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

    if (this.type !== WorkflowType.Base) {
      if (this.type !== WorkflowType.Start) {
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
    }

    return anchors
  }
}
export { AppNodeModel, AppNode }
