<template>
  <div>
    <!-- 搜索 -->
    <el-card
      class="workflow-search"
      v-if="showSearch"
      shadow="always"
      style="--el-card-padding: 8px 12px; --el-card-border-radius: 8px"
    >
      <div class="workflow-search-container flex-between">
        <el-input
          ref="searchInputRef"
          v-bind:modelValue="searchText"
          @update:modelValue="handleSearch"
          :placeholder="$t('workflow.tip.searchPlaceholder')"
          clearable
          @keyup.enter="next"
          @keyup.esc="closeSearch"
        >
        </el-input>
        <span>
          <el-space :size="4">
            <span class="lighter" v-if="selectedCount && selectedCount > 0">
              {{ currentIndex + 1 }}/{{ selectedCount }}
            </span>
            <span
              class="lighter color-secondary"
              style="width: 42px"
              v-else-if="searchText.length > 0"
            >
              无结果
            </span>
            <el-divider direction="vertical" />

            <el-button text>
              <el-icon @click="up"><ArrowUp /></el-icon>
            </el-button>
            <el-button text>
              <el-icon @click="next"><ArrowDown /></el-icon>
            </el-button>
            <el-button text @click="closeSearch()">
              <el-icon><Close /></el-icon>
            </el-button>
          </el-space>
        </span>
      </div>
    </el-card>
    <!-- 开启搜索按钮 -->
    <el-button v-else @click="openSearch()" circle class="workflow-search-button" size="large">
      <el-icon :size="20"><Search /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
// Props定义
interface Props {
  lf?: any
}
const props = withDefaults(defineProps<Props>(), {})

// 状态
const showSearch = ref(false)
const searchText = ref('')
const searchInputRef = ref<any>(null)

// 快捷键处理
const handleKeyDown = (e: KeyboardEvent) => {
  // Ctrl+F 或 Cmd+F (Mac)
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
    e.preventDefault() // 阻止浏览器默认搜索
    openSearch()
  }

  // 按ESC关闭
  if (e.key === 'Escape' && showSearch.value) {
    closeSearch()
  }
}

const focusOn = (node: any) => {
  props.lf?.graphModel.transformModel.focusOn(
    node.x,
    node.y,
    props.lf?.container.clientWidth,
    props.lf?.container.clientHeight,
  )
}
const selectedNodes = ref<Array<any>>()
const currentIndex = ref<number>(0)
const selectedCount = computed(() => {
  return selectedNodes.value?.length
})

const getSelectNodes = (kw: string) => {
  const result: Array<any> = []
  const graph_data = props.lf?.getGraphData()
  graph_data.nodes.filter((node: any) => {
    if (node.properties.stepName.includes(kw)) {
      if (node.type !== 'loop-body-node') {
        result.push({
          ...node,
          order: 1,
          focusOn: () => {
            focusOn(node)
            props.lf?.graphModel.getNodeModelById(node.id)?.focusOn(searchText.value)
          },
          selectOn: () => {
            props.lf?.graphModel.getNodeModelById(node.id)?.selectOn(searchText.value)
          },
          clearSelectOn: () => {
            props.lf?.graphModel.getNodeModelById(node.id)?.clearSelectOn(searchText.value)
          },
        })
      }
    }
    if (node.type == 'loop-body-node') {
      const nodeModel = props.lf?.graphModel
      const childNodeModel = nodeModel.getNodeModelById(node.id)
      childNodeModel.getSelectNodes(searchText.value).map((childNode: any) => {
        result.push({
          ...childNode,
          order: 2,
          focusOn: () => {
            focusOn(node)
            childNodeModel.focusOn({ node: childNode, kw: searchText.value })
          },
          selectOn: () => {
            childNodeModel.selectOn({ node: childNode, kw: searchText.value })
          },
          clearSelectOn: () => {
            childNodeModel.clearSelectOn({ node: childNode, kw: searchText.value })
          },
        })
      })
    }
  })
  result.sort((a, b) => a.order - b.order || a.y - b.y || a.x - b.x)
  return result
}
const selectNodes = (nodes: Array<any>) => {
  nodes.forEach((node) => node.selectOn())
}
const next = () => {
  if (selectedNodes.value && selectedNodes.value.length > 0) {
    selectedNodes.value[currentIndex.value]?.selectOn()
    if (selectedNodes.value.length - 1 >= currentIndex.value + 1) {
      currentIndex.value++
    } else {
      currentIndex.value = 0
    }
    selectedNodes.value[currentIndex.value]?.focusOn()
  }
}
const up = () => {
  if (selectedNodes.value && selectedNodes.value.length > 0) {
    selectedNodes.value[currentIndex.value]?.selectOn()
    if (currentIndex.value - 1 < 0) {
      currentIndex.value = selectedNodes.value.length - 1
    } else {
      currentIndex.value--
    }
    selectedNodes.value[currentIndex.value]?.focusOn()
  }
}

const onSearch = (kw: string) => {
  if (selectedNodes.value === undefined) {
    const selected = getSelectNodes(kw)
    if (selected && selected.length > 0) {
      selectedNodes.value = selected
      selectNodes(selected)
      selected[currentIndex.value].focusOn()
    }
  }
}
// 打开搜索
const openSearch = () => {
  showSearch.value = true
  searchText.value = ''

  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// 关闭搜索
const closeSearch = () => {
  clearSelect()
  showSearch.value = false
  searchText.value = ''
}
const clearSelect = () => {
  if (selectedNodes.value) {
    selectedNodes.value.forEach((node) => {
      node.clearSelectOn()
    })
  }
  selectedNodes.value = undefined
  currentIndex.value = 0
  props.lf?.graphModel.clearSelectElements()
  const graph_data = props.lf?.getGraphData()
  graph_data.nodes.forEach((node: any) => {
    if (node.type == 'loop-body-node') {
      props.lf?.graphModel.getNodeModelById(node.id).clearSelectElements()
    }
  })
}
// 执行搜索
const handleSearch = (kw: string) => {
  searchText.value = kw
  clearSelect()

  if (searchText.value.trim()) {
    onSearch?.(searchText.value)
  }
}
const reSearch = () => {
  console.log('ss')
  handleSearch(searchText.value)
}
// 生命周期
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
defineExpose({ reSearch })
</script>

<style scoped>
.workflow-search-button {
  position: absolute;
  top: 72px;
  left: 24px;
  z-index: 2;
}
.workflow-search {
  position: absolute;
  top: 72px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}
.workflow-search-container {
  width: 360px;
  :deep(.el-input__wrapper) {
    box-shadow: none;
    padding: 0 8px 0 1px !important;
  }
}
</style>
