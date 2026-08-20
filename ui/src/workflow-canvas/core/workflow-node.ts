import type { Component } from 'vue'
import { createApp } from 'vue'
import {
  h as createLogicFlowElement,
  HtmlNode,
  HtmlNodeModel,
  type GraphModel,
  type IHtmlNodeProperties,
  type Model,
} from '@logicflow/core'
import { BasicComponentsNode } from '@/workflow-canvas/config/node-mapping'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'
import { connect, disconnect } from './teleport'

type NodeViewProps = ConstructorParameters<typeof HtmlNode>[0]
type NodeFieldGroup = Record<string, WorkflowNodeField[]>

type WorkflowNodeConfig = {
  chatFields?: WorkflowNodeField[]
  fields?: WorkflowNodeField[]
  globalFields?: WorkflowNodeField[]
}

interface WorkflowNodeProperties extends IHtmlNodeProperties {
  api_input_field_list?: unknown[]
  chat_input_field_list?: unknown[]
  config?: WorkflowNodeConfig
  node_data?: unknown
  showNode?: boolean
  status?: number
  stepName?: string
  user_input_field_list?: unknown[]
}

export class WorkflowNodeView extends HtmlNode {
  private nodeApp?: ReturnType<typeof createApp>
  private readonly vueComponent: Component

  constructor(props: NodeViewProps, vueComponent: Component) {
    super(props)
    this.vueComponent = vueComponent

    const nodeModel = props.model as unknown as WorkflowNodeModel
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
              const nodeModel = this.props.model as unknown as WorkflowNodeModel
              nodeModel.openNodeMenu?.(anchorData)
            }
          },
        }),
      ],
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
  protected renderVueComponent(root: any) {
    const { model, graphModel } = this.props
    if (root) {
      connect(this.targetId(), this.vueComponent, root, () =>
        this.props.graphModel.get_provide(reactive(model), reactive(graphModel)),
      )
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

  getNodeFieldList(): WorkflowNodeField[] {
    const config = this.properties.config ?? {}
    const fields = [...(config.fields ?? [])]
    const fieldGroups: WorkflowNodeField[] = []

    if (String(this.type) === WorkflowNodeType.Start) {
      fieldGroups.push({
        value: 'global',
        label: '全局变量',
        type: 'global',
        children: config.globalFields ?? [],
      })
      fieldGroups.push({
        value: 'chat',
        label: '会话变量',
        type: 'chat',
        children: config.chatFields ?? [],
      })
    }

    fieldGroups.push({
      value: this.id,
      label: String(this.properties.stepName ?? this.type),
      type: String(this.type),
      children: fields,
    })
    return fieldGroups
  }

  getUpNodeFieldDict(containSelf: boolean, useCache: boolean): NodeFieldGroup {
    if (!this.upNodeFieldDict || !useCache) {
      this.upNodeFieldDict = this.graphModel
        .getNodeIncomingNode(this.id)
        .filter((node) => node.id !== WorkflowNodeType.Start)
        .reduce<NodeFieldGroup>((fieldGroups, node) => {
          const upstreamModel = node as unknown as WorkflowNodeModel
          return {
            ...fieldGroups,
            ...upstreamModel.getUpNodeFieldDict(true, useCache),
          }
        }, {})
    }

    if (!containSelf) return this.upNodeFieldDict
    return {
      ...this.upNodeFieldDict,
      [this.id]: this.getNodeFieldList(),
    }
  }

  getUpNodeFieldList(containSelf: boolean, useCache: boolean): WorkflowNodeField[] {
    const upstreamFields = Object.values(this.getUpNodeFieldDict(containSelf, useCache)).flat()
    const startNodeModel = this.graphModel.getNodeModelById(WorkflowNodeType.Start) as unknown as
      | WorkflowNodeModel
      | undefined
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
