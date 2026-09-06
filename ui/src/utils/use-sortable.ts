/** 基于 VueDraggablePlus 提供列表排序、动态容器绑定和可选的独立数据写回。 */
import { computed, onBeforeUnmount, onMounted, onUpdated, toValue, watch, type MaybeRefOrGetter, type Ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useDraggable, type UseDraggableOptions } from 'vue-draggable-plus'

export interface SortableChange<T> {
  oldIndex: number
  newIndex: number
  data: T[]
}

export interface SortableOptions<T> extends Omit<UseDraggableOptions<T>, 'immediate' | 'customUpdate' | 'group'> {
  /** LogicFlow 等可观察树写回时开启；普通 Vue 列表默认保持行对象引用。 */
  cloneOnUpdate?: boolean
  onReorder?: (change: SortableChange<T>) => void
}

/**
 * 绑定同一列表的拖拽排序。容器直属可拖动元素必须与数据逐项对应，并使用稳定 key。
 * target 支持模板 ref 或获取内部容器的 getter；v-if 重建后自动重新绑定。
 * 数组顺序由库更新，onReorder 仅用于保存、通知等业务处理，不应再次移动数组。
 */
export function useSortable<T>(
  target: MaybeRefOrGetter<HTMLElement | null | undefined>,
  rows: Ref<T[]>,
  options: MaybeRefOrGetter<SortableOptions<T>> = {},
) {
  let reorderedRows: T[] = []
  const sortableRows = computed({
    get: () => rows.value,
    set: (value: T[]) => {
      reorderedRows = toValue(options).cloneOnUpdate ? cloneDeep(value) : value
      rows.value = reorderedRows
    },
  })
  const draggableOptions = computed<UseDraggableOptions<T>>(() => {
    const { cloneOnUpdate: _cloneOnUpdate, onReorder, onUpdate, ...settings } = toValue(options)
    return {
      animation: 150,
      ghostClass: 'opacity-40',
      clone: cloneDeep,
      ...settings,
      immediate: false,
      onUpdate(event) {
        const { oldDraggableIndex: oldIndex, newDraggableIndex: newIndex } = event
        if (oldIndex !== undefined && newIndex !== undefined && oldIndex !== newIndex) {
          onReorder?.({ oldIndex, newIndex, data: reorderedRows })
        }
        onUpdate?.(event)
      },
    }
  })
  const draggable = useDraggable<T>(undefined, sortableRows, draggableOptions)
  let currentTarget: HTMLElement | null | undefined

  /** 在组件外部改变内部 DOM 时，可手动重新检查容器。 */
  function refresh() {
    const nextTarget = toValue(target)
    if (nextTarget === currentTarget) return
    draggable.destroy()
    currentTarget = nextTarget
    if (nextTarget) draggable.start(nextTarget)
  }

  watch(() => toValue(target), refresh, { flush: 'post' })
  onMounted(refresh)
  onUpdated(refresh)
  onBeforeUnmount(() => {
    draggable.destroy()
    currentTarget = undefined
  })

  return { pause: draggable.pause, resume: draggable.resume, refresh }
}
