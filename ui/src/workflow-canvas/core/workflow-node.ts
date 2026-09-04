import { createApp, reactive, shallowReactive, type Component } from 'vue'
import { cloneDeep } from 'lodash'
import {
  Component as LogicFlowComponent,
  createRef,
  h as createLogicFlowElement,
  HtmlNode,
  HtmlNodeModel,
  type GraphModel,
  type IHtmlNodeProperties,
  type Model,
} from '@logicflow/core'
import { nodeDict } from '@/workflow-canvas/config/node-mapping'
import { WorkflowKind, WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'
import { connect, disconnect } from './teleport'
import NodeAnchor from './node-container/NodeAnchor.vue'

type NodeViewProps = ConstructorParameters<typeof HtmlNode>[0]
type NodeFieldGroup = Record<string, WorkflowNodeField[]>
type RefreshableEdgeModel = { updatePathByAnchor?: () => void }

type WorkflowNodeConfig = { chatFields?: WorkflowNodeField[]; fields?: WorkflowNodeField[]; globalFields?: WorkflowNodeField[] }

interface WorkflowNodeProperties extends IHtmlNodeProperties {
  api_input_field_list?: unknown[]
  chat_input_field_list?: unknown[]
  config?: WorkflowNodeConfig
  enableException?: boolean
  kind?: WorkflowKind
  node_data?: unknown
  showNode?: boolean
  status?: number
  stepName?: string
  user_input_field_list?: unknown[]
}

/** 将 LogicFlow 锚点的挂载、更新和卸载同步到 Vue 组件。 */
class WorkflowNodeAnchor extends LogicFlowComponent<InstanceType<typeof NodeAnchor>['$props']> {
  private readonly containerRef = createRef<HTMLDivElement>()
  private readonly anchorProps = shallowReactive({ ...this.props })
  private readonly teleportId = `${this.props.nodeModel.graphModel.flowId}:${this.props.nodeModel.id}:anchor:${this.props.anchorData.id}`

  componentDidMount() {
    if (this.containerRef.current) {
      connect(this.teleportId, NodeAnchor, this.containerRef.current, () => ({}), this.anchorProps)
    }
  }

  componentDidUpdate() {
    Object.assign(this.anchorProps, this.props)
  }

  componentWillUnmount() {
    disconnect(this.teleportId)
  }

  render() {
    return createLogicFlowElement('div', { ref: this.containerRef })
  }
}

export class WorkflowNodeView extends HtmlNode {
  private nodeApp?: ReturnType<typeof createApp>
  private readonly vueComponent: Component

  constructor(props: NodeViewProps, vueComponent: Component) {
    super(props)
    this.vueComponent = vueComponent

    const nodeModel = props.model as unknown as WorkflowNodeModel
    const definition = nodeDict[nodeModel.type as WorkflowNodeType]
    if (definition && !nodeModel.properties.config) {
      nodeModel.properties.config = cloneDeep(definition.properties?.config ?? {})
    }
    nodeModel.properties.stepName = this.getUniqueNodeName(
      props.graphModel,
      String(nodeModel.properties.stepName ?? definition?.label ?? nodeModel.type),
      nodeModel.id,
    )
  }

  private getUniqueNodeName(graphModel: GraphModel, baseName: string, nodeId: string) {
    const names = new Set(graphModel.nodes.filter((node) => node.id !== nodeId).map((node) => String(node.properties.stepName ?? '')))
    let index = 0
    let nodeName = baseName
    while (names.has(nodeName.trim())) nodeName = `${baseName}${++index}`
    return nodeName
  }

  getAnchors() {
    if (!this.props.model.isHittable) return []
    return super.getAnchors()
  }

  getAnchorShape(anchorData?: Model.AnchorConfig) {
    if (!anchorData) return null
    const { x, y, type } = anchorData
    const nodeModel = this.props.model as unknown as WorkflowNodeModel
    const canOpenNodeMenu = type === 'right' && typeof nodeModel.openNodeMenu === 'function'
    const connected = this.props.graphModel.edges.some((edge) =>
      type === 'left' ? edge.targetAnchorId === anchorData.id : edge.sourceAnchorId === anchorData.id,
    )

    return createLogicFlowElement(
      'foreignObject',
      { ...anchorData, className: 'workflow-node-anchor-wrapper', x: x - 12, y: y - 12, width: 24, height: 24 },
      [createLogicFlowElement(WorkflowNodeAnchor, { key: anchorData.id, anchorData, canOpenNodeMenu, connected, nodeModel })],
    )
  }

  setHtml(rootEl: SVGForeignObjectElement) {
    if (this.nodeApp) return
    if (!rootEl.innerHTML) {
      const node = document.createElement('div')
      node.setAttribute('data-node-id', this.props.model.id)
      node.setAttribute('data-node-type', this.props.model.type)
      rootEl.appendChild(node)
      this.renderVueComponent(node)
    }
  }
  protected renderVueComponent(root: HTMLDivElement) {
    const { model, graphModel } = this.props
    if (root) {
      connect(this.targetId(), this.vueComponent, root, () => this.props.graphModel.get_provide(reactive(model), reactive(graphModel)))
    }
  }
  protected targetId() {
    return `${this.props.graphModel.flowId}:${this.props.model.id}`
  }

  componentWillUnmount() {
    super.componentWillUnmount()
    disconnect(this.targetId())
  }
}

export class WorkflowNodeModel extends HtmlNodeModel<WorkflowNodeProperties> {
  private upNodeFieldDict?: NodeFieldGroup

  openNodeMenu?: (anchorData: Model.AnchorConfig) => void
  validate?: () => Promise<unknown>

  setAttributes() {
    this.width = Number(this.properties.width ?? 320)
    this.height = Number(this.properties.height ?? 300)
    this.text.editable = false
  }

  setHeight(nodeHeight: number) {
    const targetHeight = Math.max(nodeHeight, 1)
    if (targetHeight === this.height) return
    const offset = (targetHeight - this.height) / 2
    this.height = targetHeight
    this.properties.height = targetHeight
    this.move(0, offset)
    const connectedEdges = new Set([...this.incoming.edges, ...this.outgoing.edges])
    connectedEdges.forEach((edge) => {
      const refreshableEdge = edge as unknown as RefreshableEdgeModel
      refreshableEdge.updatePathByAnchor?.()
    })
  }

  getNodeFieldList(): WorkflowNodeField[] {
    const config = this.properties.config ?? {}
    const fields = [...(config.fields ?? [])]
    const fieldGroups: WorkflowNodeField[] = []

    if (String(this.type) === WorkflowNodeType.Start) {
      fieldGroups.push({ value: 'global', label: '全局变量', type: 'global', children: config.globalFields ?? [] })
      fieldGroups.push({ value: 'chat', label: '会话变量', type: 'chat', children: config.chatFields ?? [] })
    }

    fieldGroups.push({ value: this.id, label: String(this.properties.stepName ?? this.type), type: String(this.type), children: fields })
    return fieldGroups
  }

  getUpNodeFieldDict(containSelf: boolean, useCache: boolean): NodeFieldGroup {
    if (!this.upNodeFieldDict || !useCache) {
      this.upNodeFieldDict = this.graphModel
        .getNodeIncomingNode(this.id)
        .filter((node) => node.id !== WorkflowNodeType.Start)
        .reduce<NodeFieldGroup>((fieldGroups, node) => {
          const upstreamModel = node as unknown as WorkflowNodeModel
          return { ...fieldGroups, ...upstreamModel.getUpNodeFieldDict(true, useCache) }
        }, {})
    }

    if (!containSelf) return this.upNodeFieldDict
    return { ...this.upNodeFieldDict, [this.id]: this.getNodeFieldList() }
  }

  getUpNodeFieldList(containSelf: boolean, useCache: boolean): WorkflowNodeField[] {
    const upstreamFields = Object.values(this.getUpNodeFieldDict(containSelf, useCache)).flat()
    const startNodeModel = this.graphModel.getNodeModelById(WorkflowNodeType.Start) as unknown as WorkflowNodeModel | undefined
    return [...(startNodeModel?.getNodeFieldList() ?? []), ...upstreamFields]
  }

  clearNextNodeField(containSelf: boolean) {
    this.graphModel.getNodeOutgoingNode(this.id).forEach((node) => {
      const downstreamModel = node as unknown as WorkflowNodeModel
      downstreamModel.clearNextNodeField(true)
    })
    if (containSelf) this.upNodeFieldDict = undefined
  }

  getDefaultAnchor(): Model.AnchorConfig[] {
    const { id, x, y, width } = this
    const showNode = this.properties.showNode === undefined ? true : this.properties.showNode
    const anchors: Model.AnchorConfig[] = []

    if ([WorkflowNodeType.Base, WorkflowNodeType.KnowledgeBase, WorkflowNodeType.ToolBaseNode].some((nodeType) => nodeType === String(this.type))) {
      return anchors
    }

    if (
      ![WorkflowNodeType.Start, WorkflowNodeType.LoopStartNode, WorkflowNodeType.ToolStartNode].some((nodeType) => nodeType === String(this.type)) &&
      this.properties.kind !== WorkflowKind.DataSource
    ) {
      anchors.push({ x: x - width / 2, y: showNode ? y : y, id: `${id}_left`, type: 'left', edgeAddable: false })
    }

    if (this.properties.enableException) {
      anchors.push({ x: x + width / 2, y: y + this.height / 2 - 40, id: `${id}_exception_right`, type: 'right' })
    }
    anchors.push({ x: x + width / 2, y: showNode ? y : y, id: `${id}_right`, type: 'right' })
    return anchors
  }

  getNodeStyle() {
    return { ...super.getNodeStyle(), stroke: 'transparent' }
  }

  getOutlineStyle() {
    return { ...super.getOutlineStyle(), stroke: 'transparent' }
  }
}
