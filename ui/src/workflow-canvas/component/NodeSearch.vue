<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from 'vue'
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
  currentIndex.value = (currentIndex.value + direction + matchedNodes.value.length) % matchedNodes.value.length
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
  <el-button
    :type="searchVisible ? 'primary' : 'default'"
    text
    :style="{ background: searchVisible ? 'var(--mk-primary-transparent-10)' : 'transparent' }"
    @click="openSearch"
  >
    <MkIcon name="icon_search-outlined" size="18" />
  </el-button>
  <el-card v-if="searchVisible" shadow="always" class="workflow-search-container" style="--el-card-padding: 8px 12px">
    <div class="flex items-center gap-1">
      <el-input ref="searchInputRef" v-model="searchKeyword" clearable placeholder="请输入节点名称" @keyup.enter="searchNext(1)" />
      <span class="shrink-0">
        {{ matchedNodes.length ? `${currentIndex + 1}/${matchedNodes.length}` : searchKeyword && '无结果' }}
      </span>
      <el-divider direction="vertical" class="mx-2!" />
      <el-button text @click="searchNext(-1)"><MkIcon name="icon_up_outlined" /></el-button>
      <el-button text @click="searchNext(1)"><MkIcon name="icon_down_outlined" /></el-button>
      <el-button text @click="closeSearch"><MkIcon name="icon_close_outlined" /></el-button>
    </div>
  </el-card>
</template>

<style scoped lang="scss">
.workflow-search-container {
  left: 50%;
  position: fixed;
  top: 96px;
  transform: translate(-50%, -50%);
  z-index: 10;
  width: 380px;

  :deep(.el-input__wrapper) {
    box-shadow: none;
    padding: 0;
  }
}
</style>
