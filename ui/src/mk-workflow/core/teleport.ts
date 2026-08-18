import type { BaseEdgeModel, BaseNodeModel, GraphModel } from '@logicflow/core'
import type { Component } from 'vue'
import { defineComponent, Fragment, h, markRaw, reactive, Teleport } from 'vue'

type TeleportModel = BaseNodeModel | BaseEdgeModel
type ComponentProps = Record<string, unknown>
type ProvideValues = Record<string, unknown>
type GetComponentProps = (node: TeleportModel, graph: GraphModel) => ComponentProps
type GetProvideValues = (node: TeleportModel, graph: GraphModel) => ProvideValues

let active = false
const teleportItems = reactive<Record<string, Component>>({})

export function connect(
  id: string,
  component: Component,
  container: HTMLDivElement,
  node: TeleportModel,
  graph: GraphModel,
  getComponentProps: GetComponentProps = (currentNode, currentGraph) => ({
    nodeModel: currentNode,
    graph: currentGraph,
  }),
  getProvideValues: GetProvideValues = (currentNode, currentGraph) => ({
    getNode: () => currentNode,
    getGraph: () => currentGraph,
  }),
) {
  if (!active) return

  teleportItems[id] = markRaw(
    defineComponent({
      name: 'WorkflowTeleportItem',
      provide: () => getProvideValues(node, graph),
      render: () => h(Teleport, { to: container }, [h(component, getComponentProps(node, graph))]),
    }),
  )
}

export function disconnect(id: string) {
  if (active) delete teleportItems[id]
}

export function disconnectByFlow(flowId: string) {
  Object.keys(teleportItems).forEach((id) => {
    if (id.startsWith(flowId)) delete teleportItems[id]
  })
}

export function disconnectAll() {
  Object.keys(teleportItems).forEach((id) => delete teleportItems[id])
}

export function isActive() {
  return active
}

export function getTeleport() {
  active = true
  return defineComponent({
    name: 'WorkflowTeleportContainer',
    props: {
      flowId: {
        type: String,
        required: true,
      },
    },
    setup() {
      return () =>
        h(
          Fragment,
          {},
          Object.values(teleportItems).map((component) => h(component)),
        )
    },
  })
}
