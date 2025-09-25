import { BaseEdgeModel, BaseNodeModel, GraphModel } from '@logicflow/core'
import { defineComponent, h, reactive, isVue3, Teleport, markRaw, Fragment } from 'vue-demi'

let active = false
const items = reactive<{ [key: string]: any }>({})

export function connect(
  id: string,
  component: any,
  container: HTMLDivElement,
  node: BaseNodeModel | BaseEdgeModel,
  graph: GraphModel,
  get_props?: any,
  get_provide?: any,
) {
  if (!get_props) {
    get_props = (node: BaseNodeModel | BaseEdgeModel, graph: GraphModel) => {
      return { nodeModel: node, graph }
    }
  }
  if (!get_provide) {
    get_provide = (node: BaseNodeModel | BaseEdgeModel, graph: GraphModel) => ({
      getNode: () => node,
      getGraph: () => graph,
    })
  }
  if (active) {
    items[id] = markRaw(
      defineComponent({
        render: () => h(Teleport, { to: container } as any, [h(component, get_props(node, graph))]),
        provide: () => get_provide(node, graph),
      }),
    )
  }
}

export function disconnect(id: string) {
  if (active) {
    delete items[id]
  }
}

export function isActive() {
  return active
}

export function getTeleport(): any {
  if (!isVue3) {
    throw new Error('teleport is only available in Vue3')
  }
  active = true

  return defineComponent({
    props: {
      flowId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      return () => {
        const children: Record<string, any>[] = []
        Object.keys(items).forEach((id) => {
          // https://github.com/didi/LogicFlow/issues/1768
          // 多个不同的VueNodeView都会connect注册到items中，因此items存储了可能有多个flowId流程图的数据
          // 当使用多个LogicFlow时，会创建多个flowId + 同时使用KeepAlive
          // 每一次items改变，会触发不同flowId持有的setup()执行，由于每次setup()执行就是遍历items，因此存在多次重复渲染元素的问题
          // 即items[0]会在Page1的setup()执行，items[0]也会在Page2的setup()执行，从而生成两个items[0]

          // 比对当前界面显示的flowId，只更新items[当前页面flowId:nodeId]的数据
          // 比如items[0]属于Page1的数据，那么Page2无论active=true/false，都无法执行items[0]

          children.push(items[id])
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
