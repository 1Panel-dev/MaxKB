import type { Component } from 'vue'
import { createApp, h as createVNode } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import {
  h as createLogicFlowElement,
  HtmlNode,
  HtmlNodeModel,
  type GraphModel,
  type IHtmlNodeProperties,
  type Model,
} from '@logicflow/core'
import { BasicComponentsNode } from '@/mk-workflow/core/data'
import { WorkflowNodeType } from '@/mk-workflow/types'

type NodeViewProps = ConstructorParameters<typeof HtmlNode>[0]
type NodeFieldGroup = Record<string, Array<Record<string, unknown>>>
export type WorkflowNodeConfig = {
  chatFields?: Array<Record<string, unknown>>
  fields?: Array<Record<string, unknown>>
  globalFields?: Array<Record<string, unknown>>
}

export interface WorkflowNodeProperties extends IHtmlNodeProperties {
  api_input_field_list?: unknown[]
  chat_input_field_list?: unknown[]
  config?: WorkflowNodeConfig
  node_data?: unknown
  showNode?: boolean
  status?: number
  stepName?: string
  user_input_field_list?: unknown[]
}

export class AppNode extends HtmlNode {
  private nodeApp?: ReturnType<typeof createApp>
  private readonly vueComponent: Component

  constructor(props: NodeViewProps, vueComponent: Component) {
    super(props)
    this.vueComponent = vueComponent

    const nodeModel = props.model as unknown as AppNodeModel
    nodeModel.clear_next_node_field = this.clearNextNodeField.bind(this)
    nodeModel.get_node_field_list = this.getNodeFieldList.bind(this)
    nodeModel.get_up_node_field_dict = this.getUpNodeFieldDict.bind(this)
    nodeModel.get_up_node_field_list = this.getUpNodeFieldList.bind(this)

    const definition = BasicComponentsNode[nodeModel.type as WorkflowNodeType]
    if (definition && !nodeModel.properties.config) {
      nodeModel.properties.config = structuredClone(definition.properties.config ?? {})
    }
    nodeModel.properties.stepName = this.getUniqueNodeName(
      props.graphModel,
      String(nodeModel.properties.stepName ?? definition?.label ?? nodeModel.type),
      nodeModel.id,
    )
  }

  private getUniqueNodeName(graphModel: GraphModel, baseName: string, nodeId: string) {
    const names = new Set(
      graphModel.nodes
        .filter((node) => node.id !== nodeId)
        .map((node) => String(node.properties.stepName ?? '')),
    )
    let index = 0
    let nodeName = baseName
    while (names.has(nodeName.trim())) nodeName = `${baseName}${++index}`
    return nodeName
  }

  private getNodeFieldList() {
    const nodeModel = this.props.model as unknown as AppNodeModel
    const config = nodeModel.properties.config ?? {}
    const fields = [...(config.fields ?? [])]
    const result: Array<Record<string, unknown>> = []

    if (String(nodeModel.type) === WorkflowNodeType.Start) {
      result.push({
        value: 'global',
        label: '全局变量',
        type: 'global',
        children: config.globalFields ?? [],
      })
      result.push({
        value: 'chat',
        label: '会话变量',
        type: 'chat',
        children: config.chatFields ?? [],
      })
    }

    result.push({
      value: nodeModel.id,
      label: nodeModel.properties.stepName,
      type: nodeModel.type,
      children: fields,
    })
    return result
  }

  private getUpNodeFieldDict(containSelf: boolean, useCache: boolean): NodeFieldGroup {
    const nodeModel = this.props.model as unknown as AppNodeModel
    if (!nodeModel.upNodeFieldDict || !useCache) {
      nodeModel.upNodeFieldDict = nodeModel.graphModel
        .getNodeIncomingNode(nodeModel.id)
        .filter((node) => node.id !== WorkflowNodeType.Start)
        .reduce<NodeFieldGroup>((fieldGroups, node) => {
          const upstreamModel = node as unknown as AppNodeModel
          return {
            ...fieldGroups,
            ...upstreamModel.get_up_node_field_dict?.(true, useCache),
          }
        }, {})
    }

    if (!containSelf) return nodeModel.upNodeFieldDict
    return {
      ...nodeModel.upNodeFieldDict,
      [nodeModel.id]: this.getNodeFieldList(),
    }
  }

  private getUpNodeFieldList(containSelf: boolean, useCache: boolean) {
    const nodeModel = this.props.model as unknown as AppNodeModel
    const upstreamFields = Object.values(this.getUpNodeFieldDict(containSelf, useCache)).flat()
    const startFields = (
      nodeModel.graphModel.getNodeModelById(WorkflowNodeType.Start) as unknown as
        | AppNodeModel
        | undefined
    )?.get_node_field_list?.()
    return [...(startFields ?? []), ...upstreamFields]
  }

  private clearNextNodeField(containSelf: boolean) {
    const nodeModel = this.props.model as unknown as AppNodeModel
    nodeModel.graphModel.getNodeOutgoingNode(nodeModel.id).forEach((node) => {
      ;(node as unknown as AppNodeModel).clear_next_node_field?.(true)
    })
    if (containSelf) nodeModel.upNodeFieldDict = undefined
  }

  getAnchorShape(anchorData?: Model.AnchorConfig) {
    if (!anchorData) return null
    const { x, y, type } = anchorData
    const connected = this.props.graphModel.edges.some((edge) =>
      type === 'left'
        ? edge.targetAnchorId === anchorData.id
        : edge.sourceAnchorId === anchorData.id,
    )

    return createLogicFlowElement(
      'foreignObject',
      { ...anchorData, x: x - 10, y: y - 10, width: 20, height: 20 },
      [
        createLogicFlowElement('div', {
          className: 'h-5 w-5 cursor-pointer rounded-full border-2 border-primary bg-white',
          style: connected ? { background: 'var(--mk-primary)' } : {},
          onClick: () => {
            if (type === 'right') {
              ;(this.props.model as unknown as AppNodeModel).openNodeMenu?.(anchorData)
            }
          },
        }),
      ],
    )
  }

  setHtml(rootElement: SVGForeignObjectElement) {
    if (this.nodeApp) return
    const mountElement = document.createElement('div')
    rootElement.replaceChildren(mountElement)
    const nodeModel = this.props.model

    this.nodeApp = createApp({
      render: () => createVNode(this.vueComponent, { nodeModel }),
    })
    this.nodeApp.use(ElementPlus, { locale: zhCn })
    this.nodeApp.mount(mountElement)
  }

  componentWillUnmount() {
    super.componentWillUnmount()
    this.nodeApp?.unmount()
    this.nodeApp = undefined
  }
}

export class AppNodeModel extends HtmlNodeModel<WorkflowNodeProperties> {
  upNodeFieldDict?: NodeFieldGroup
  clear_next_node_field?: (containSelf: boolean) => void
  get_node_field_list?: () => Array<Record<string, unknown>>
  get_up_node_field_dict?: (containSelf: boolean, useCache: boolean) => NodeFieldGroup
  get_up_node_field_list?: (
    containSelf: boolean,
    useCache: boolean,
  ) => Array<Record<string, unknown>>
  openNodeMenu?: (anchorData: Model.AnchorConfig) => void
  validate?: () => Promise<unknown>

  setAttributes() {
    this.width = Number(
      this.properties.width ?? (String(this.type) === WorkflowNodeType.Base ? 600 : 340),
    )
    this.height = Number(this.properties.height ?? 300)
    this.text.editable = false
  }

  setHeight(contentHeight: number) {
    const targetHeight = Math.max(contentHeight + 32, 120)
    if (targetHeight === this.height) return
    const offset = (targetHeight - this.height) / 2
    this.height = targetHeight
    this.properties.height = targetHeight
    this.move(0, offset)
  }

  getDefaultAnchor(): Model.AnchorConfig[] {
    if (String(this.type) === WorkflowNodeType.Base) return []

    const anchors: Model.AnchorConfig[] = []
    if (String(this.type) !== WorkflowNodeType.Start) {
      anchors.push({
        x: this.x - this.width / 2,
        y: this.y,
        id: `${this.id}_left`,
        type: 'left',
        edgeAddable: false,
      })
    }
    anchors.push({
      x: this.x + this.width / 2,
      y: this.y,
      id: `${this.id}_right`,
      type: 'right',
    })
    return anchors
  }

  getNodeStyle() {
    return { ...super.getNodeStyle(), stroke: 'transparent' }
  }

  getOutlineStyle() {
    return { ...super.getOutlineStyle(), stroke: 'transparent' }
  }
}
