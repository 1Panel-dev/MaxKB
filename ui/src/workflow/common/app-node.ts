import Components from '@/components'
import ElementPlus from 'element-plus'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { HtmlResize } from '@logicflow/extension'
import { h as lh } from '@logicflow/core'
import { createApp, h } from 'vue'
import directives from '@/directives'
import i18n from '@/locales'
import { WorkflowType } from '@/enums/application'
import { nodeDict } from '@/workflow/common/data'
import { isActive, connect, disconnect } from './teleport'
import { t } from '@/locales'
import { type Dict } from '@/api/type/common'
const getNodeName = (nodes: Array<any>, baseName: string) => {
  let index = 0
  let name = baseName
  while (true) {
    if (index > 0) {
      name = baseName + index
    }
    if (!nodes.some((node: any) => node.properties.stepName === name.trim())) {
      return name
    }
    index++
  }
}
class AppNode extends HtmlResize.view {
  isMounted
  r?: any
  component: any
  app: any
  root?: any
  VueNode: any
  up_node_field_dict?: Dict<Array<any>>
  constructor(props: any, VueNode: any) {
    super(props)
    this.component = VueNode
    this.isMounted = false
    props.model.clear_next_node_field = this.clear_next_node_field.bind(this)
    props.model.get_up_node_field_dict = this.get_up_node_field_dict.bind(this)
    props.model.get_node_field_list = this.get_node_field_list.bind(this)
    props.model.get_up_node_field_list = this.get_up_node_field_list.bind(this)

    if (props.model.properties.noRender) {
      delete props.model.properties.noRender
    } else {
      props.model.properties.stepName = getNodeName(
        props.graphModel.nodes.filter((node: any) => node.id !== props.model.id),
        props.model.properties.stepName,
      )
    }

    props.model.properties.config = nodeDict[props.model.type].properties.config
    if (props.model.properties.height) {
      props.model.height = props.model.properties.height
    }
  }
  get_node_field_list() {
    const result = []
    if (this.props.model.type === 'start-node') {
      result.push({
        value: 'global',
        label: t('views.applicationWorkflow.variable.global'),
        type: 'global',
        children: this.props.model.properties?.config?.globalFields || [],
      })
      result.push({
        value: 'chat',
        label: t('views.applicationWorkflow.variable.chat'),
        type: 'chat',
        children: this.props.model.properties?.config?.chatFields || [],
      })
    }
    result.push({
      value: this.props.model.id,
      label: this.props.model.properties.stepName,
      type: this.props.model.type,
      children: this.props.model.properties?.config?.fields || [],
    })
    return result
  }
  get_up_node_field_dict(contain_self: boolean, use_cache: boolean) {
    if (!this.up_node_field_dict || !use_cache) {
      const up_node_list = this.props.graphModel.getNodeIncomingNode(this.props.model.id)
      this.up_node_field_dict = up_node_list
        .filter((node) => node.id != 'start-node' && node.id != 'loop-start-node')
        .map((node) => node.get_up_node_field_dict(true, use_cache))
        .reduce((pre, next) => ({ ...pre, ...next }), {})
    }
    if (contain_self) {
      return {
        ...this.up_node_field_dict,
        [this.props.model.id]: this.get_node_field_list(),
      }
    }
    return this.up_node_field_dict ? this.up_node_field_dict : {}
  }

  get_up_node_field_list(contain_self: boolean, use_cache: boolean) {
    const result = Object.values(this.get_up_node_field_dict(contain_self, use_cache)).reduce(
      (pre, next) => [...pre, ...next],
      [],
    )
    const start_node_field_list = (
      this.props.graphModel.getNodeModelById('start-node') ||
      this.props.graphModel.getNodeModelById('loop-start-node')
    ).get_node_field_list()
    return [...start_node_field_list, ...result]
  }

  clear_next_node_field(contain_self: boolean) {
    const next_node_list = this.props.graphModel.getNodeOutgoingNode(this.props.model.id)
    next_node_list.forEach((node) => {
      node.clear_next_node_field(true)
    })
    if (contain_self) {
      this.up_node_field_dict = undefined
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
        height: 30,
      },
      [
        lh('div', {
          style: { zindex: 0 },
          onClick: () => {
            if (type == 'right') {
              this.props.model.openNodeMenu(anchorData)
            }
          },
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
        </svg>`,
          },
        }),
      ],
    )
  }

  setHtml(rootEl: HTMLElement) {
    if (!this.isMounted) {
      this.isMounted = true
      const node = document.createElement('div')
      rootEl.appendChild(node)
      this.renderVueComponent(node)
    } else {
      if (this.r && this.r.component) {
        this.r.component.props.properties = this.props.model.getProperties()
      }
    }
  }
  componentWillUnmount() {
    super.componentWillUnmount()
    this.unmount()
  }
  getComponentContainer() {
    return this.root
  }
  protected targetId() {
    return `${this.props.graphModel.flowId}:${this.props.model.id}`
  }
  protected renderVueComponent(root: any) {
    this.unmountVueComponent()
    this.root = root
    const { model, graphModel } = this.props

    if (root) {
      if (isActive()) {
        connect(
          this.targetId(),
          this.component,
          root,
          model,
          graphModel,
          undefined,
          this.props.graphModel.get_provide,
        )
      } else {
        this.r = h(this.component, {
          properties: this.props.model.properties,
          nodeModel: this.props.model,
        })
        this.app = createApp({
          render() {
            return this.r
          },
          provide() {
            return {
              getNode: () => model,
              getGraph: () => graphModel,
            }
          },
        })

        this.app.use(ElementPlus, {
          locale: zhCn,
        })
        this.app.use(Components)
        this.app.use(directives)
        this.app.use(i18n)
        for (const [key, component] of Object.entries(ElementPlusIcons)) {
          this.app.component(key, component)
        }
        this.app?.mount(root)
      }
    }
  }

  protected unmountVueComponent() {
    if (this.app) {
      this.app.unmount()
      this.app = null
    }
    if (this.root) {
      this.root.innerHTML = ''
    }
    return this.root
  }

  unmount() {
    if (isActive()) {
      disconnect(this.targetId())
    }
    this.unmountVueComponent()
  }
}

class AppNodeModel extends HtmlResize.model {
  refreshDeges() {
    // 更新节点连接边的path
    this.incoming.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
    this.outgoing.edges.forEach((edge: any) => {
      edge.updatePathByAnchor()
    })
  }
  set_position(position: { x?: number; y?: number }) {
    const { x, y } = position
    if (x) {
      this.x = x
    }
    if (y) {
      this.y = y
    }
    this.refreshDeges()
  }
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
      overflow: 'visible',
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
  get_width() {
    return this.properties?.width || 340
  }

  setAttributes() {
    const { t } = i18n.global
    this.width = this.get_width()
    const isLoop = (node_id: string, target_node_id: string) => {
      const up_node_list = this.graphModel.getNodeIncomingNode(node_id)
      for (const index in up_node_list) {
        const item = up_node_list[index]
        if (item.id === target_node_id) {
          return true
        } else {
          const result = isLoop(item.id, target_node_id)
          if (result) {
            return true
          }
        }
      }
      return false
    }
    const circleOnlyAsTarget = {
      message: t('views.applicationWorkflow.tip.onlyRight'),
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any) => {
        return sourceAnchor.type === 'right'
      },
    }
    this.sourceRules.push({
      message: t('views.applicationWorkflow.tip.notRecyclable'),
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
        if (targetNode.id == sourceNode.id) {
          return false
        }
        const up_node_list = this.graphModel.getNodeIncomingNode(targetNode.id)
        const is_c = up_node_list.find((up_node) => up_node.id == sourceNode.id)
        return !is_c && !isLoop(sourceNode.id, targetNode.id)
      },
    })

    this.sourceRules.push(circleOnlyAsTarget)
    this.targetRules.push({
      message: t('views.applicationWorkflow.tip.onlyLeft'),
      validate: (sourceNode: any, targetNode: any, sourceAnchor: any, targetAnchor: any) => {
        return targetAnchor.type === 'left'
      },
    })
  }
  getDefaultAnchor() {
    const { id, x, y, width } = this
    const showNode = this.properties.showNode === undefined ? true : this.properties.showNode
    const anchors: any = []

    if (this.type !== WorkflowType.Base) {
      if (![WorkflowType.Start, WorkflowType.LoopStartNode.toString()].includes(this.type)) {
        anchors.push({
          x: x - width / 2 + 10,
          y: showNode ? y : y - 15,
          id: `${id}_left`,
          edgeAddable: false,
          type: 'left',
        })
      }
      anchors.push({
        x: x + width / 2 - 10,
        y: showNode ? y : y - 15,
        id: `${id}_right`,
        type: 'right',
      })
    }

    return anchors
  }
}
export { AppNodeModel, AppNode }
