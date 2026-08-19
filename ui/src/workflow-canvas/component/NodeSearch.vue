<script setup lang="ts">
import { ArrowDown, ArrowUp, Close, Search } from '@element-plus/icons-vue'
import type LogicFlow from '@logicflow/core'
import type { InputInstance } from 'element-plus'

defineOptions({ name: 'WorkflowNodeSearch' })

const props = defineProps<{ logicFlow: LogicFlow }>()
const searchInputRef = useTemplateRef<InputInstance>('searchInputRef')
const searchVisible = ref(false)
const searchKeyword = ref('')
const currentIndex = ref(0)

const matchedNodes = computed(() => {
  const keyword = searchKeyword.value.trim().toLocaleLowerCase()
  if (!keyword) return []
  return props.logicFlow.getGraphRawData().nodes.filter((node) =>
    String(node.properties?.stepName ?? '')
      .toLocaleLowerCase()
      .includes(keyword),
  )
})

function focusCurrentNode() {
  const node = matchedNodes.value[currentIndex.value]
  props.logicFlow.clearSelectElements()
  if (!node) return
  props.logicFlow.selectElementById(node.id)
  props.logicFlow.focusOn(node.id)
}

function searchNext(direction: 1 | -1) {
  if (!matchedNodes.value.length) return
  currentIndex.value =
    (currentIndex.value + direction + matchedNodes.value.length) % matchedNodes.value.length
  focusCurrentNode()
}

function openSearch() {
  searchVisible.value = true
  nextTick(() => searchInputRef.value?.focus())
}

function closeSearch() {
  searchVisible.value = false
  searchKeyword.value = ''
  currentIndex.value = 0
  props.logicFlow.clearSelectElements()
}

function handleShortcut(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase() === 'f') {
    event.preventDefault()
    openSearch()
  }
  if (event.key === 'Escape' && searchVisible.value) closeSearch()
}

watch(searchKeyword, () => {
  currentIndex.value = 0
  focusCurrentNode()
})

onMounted(() => window.addEventListener('keydown', handleShortcut))
onBeforeUnmount(() => window.removeEventListener('keydown', handleShortcut))
</script>

<template>
  <div class="absolute left-5 top-5 z-10">
    <el-button v-if="!searchVisible" circle size="large" @click="openSearch">
      <MkIcon :icon="Search" />
    </el-button>

    <div
      v-else
      class="flex w-[360px] items-center gap-1 rounded-lg border border-N300 bg-white p-2 shadow-sm"
    >
      <el-input
        ref="searchInputRef"
        v-model="searchKeyword"
        clearable
        placeholder="搜索节点名称"
        @keyup.enter="searchNext(1)"
      />
      <span class="shrink-0 text-N600">
        {{ matchedNodes.length ? `${currentIndex + 1}/${matchedNodes.length}` : '无结果' }}
      </span>
      <el-button text @click="searchNext(-1)"><MkIcon :icon="ArrowUp" /></el-button>
      <el-button text @click="searchNext(1)"><MkIcon :icon="ArrowDown" /></el-button>
      <el-button text @click="closeSearch"><MkIcon :icon="Close" /></el-button>
    </div>
  </div>
</template>
