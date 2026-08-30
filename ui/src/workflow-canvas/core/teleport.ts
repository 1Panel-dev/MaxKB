import type { BaseEdgeModel, BaseNodeModel, GraphModel } from '@logicflow/core'
import type { Component } from 'vue'
import { defineComponent, h, reactive, isVue3, Teleport, markRaw, Fragment } from 'vue-demi'

type TeleportNodeModel = BaseNodeModel | BaseEdgeModel
type TeleportProvide = Record<string | symbol, unknown>
type ProvideFactory<NodeModel extends TeleportNodeModel> = () => TeleportProvide

let active = false
const teleportItems = reactive<Record<string, Component>>({})

export function connect<NodeModel extends TeleportNodeModel>(id: string, component: Component, container: HTMLDivElement, get_provide: ProvideFactory<NodeModel>) {
  if (active) {
    teleportItems[id] = markRaw(defineComponent({ render: () => h(Teleport, { to: container }, [h(component)]), provide: () => get_provide() }))
  }
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

export function getTeleport(): Component {
  if (!isVue3) {
    throw new Error('teleport is only available in Vue3')
  }
  active = true

  return defineComponent({
    props: { flowId: { type: String, required: true } },
    setup(props) {
      return () => {
        const children: Component[] = []
        Object.keys(teleportItems).forEach((id) => {
          // https://github.com/didi/LogicFlow/issues/1768
          // 多个不同的VueNodeView都会connect注册到items中，因此items存储了可能有多个flowId流程图的数据
          // 当使用多个LogicFlow时，会创建多个flowId + 同时使用KeepAlive
          // 每一次items改变，会触发不同flowId持有的setup()执行，由于每次setup()执行就是遍历items，因此存在多次重复渲染元素的问题
          // 即items[0]会在Page1的setup()执行，items[0]也会在Page2的setup()执行，从而生成两个items[0]

          // 比对当前界面显示的flowId，只更新items[当前页面flowId:nodeId]的数据
          // 比如items[0]属于Page1的数据，那么Page2无论active=true/false，都无法执行items[0]

          const component = teleportItems[id]
          if (component) children.push(component)
        })
        return h(
          Fragment,
          {},
          children.map((item) => h(item)),
        )
      }
    },
  })
}
