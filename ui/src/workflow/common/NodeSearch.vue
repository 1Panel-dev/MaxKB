<template>
  <div>
    <!-- 搜索遮罩层 -->
    <Teleport to="body">
      <div v-if="showSearch" class="search-mask" @click.self="closeSearch">
        <div class="search-container">
          <el-input
            ref="searchInputRef"
            v-model="searchText"
            placeholder="搜索..."
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
            @keyup.esc="closeSearch"
          >
            <template #append>
              <el-button @click="closeSearch">取消</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Search } from '@element-plus/icons-vue'

// Props定义
interface Props {
  onSearch?: (keyword: string) => void // 搜索回调
}

const props = withDefaults(defineProps<Props>(), {
  useElementPlus: false,
  onSearch: undefined,
})

// 状态
const showSearch = ref(false)
const searchText = ref('')
const searchInputRef = ref<any>(null)
const nativeInputRef = ref<HTMLInputElement | null>(null)

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
  showSearch.value = false
  searchText.value = ''
}

// 执行搜索
const handleSearch = () => {
  if (searchText.value.trim()) {
    props.onSearch?.(searchText.value)
  }
}

// 生命周期
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.search-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  z-index: 9999;
  padding-top: 20vh;
}

.search-container {
  width: 500px;
  max-width: 90%;
  animation: slideDown 0.2s ease;
}

/* 原生输入框样式 */
.native-search {
  display: flex;
  gap: 8px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.native-search input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.native-search input:focus {
  border-color: #409eff;
}

.native-search button {
  padding: 0 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.native-search button:hover {
  border-color: #409eff;
  color: #409eff;
}

.content {
  padding: 20px;
}

.item {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
