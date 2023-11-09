<template>
  <div class="app-table" :class="quickCreate ? 'table-quick-append' : ''">
    <el-table v-bind="$attrs">
      <template #append v-if="quickCreate">
        <div v-if="showInput">
          <el-input
            ref="quickInputRef"
            v-model="inputValue"
            placeholder="请输入文档名称"
            class="w-240 mr-12"
          />

          <el-button type="primary" @click="submitHandle">创建</el-button>
          <el-button @click="showInput = false">取消</el-button>
        </div>
        <div v-else @click="quickCreateHandel" class="w-full">
          <el-button type="primary" link>
            <el-icon><Plus /></el-icon>
            <span class="ml-4">快速创建空白文档</span>
          </el-button>
        </div>
      </template>
      <slot></slot>
    </el-table>
    <div class="app-table__pagination mt-16" v-if="$slots.pagination || paginationConfig">
      <slot name="pagination">
        <el-pagination
          v-model:current-page="paginationConfig.currentPage"
          v-model:page-size="paginationConfig.pageSize"
          :page-sizes="pageSizes"
          :total="paginationConfig.total"
          layout="total, prev, pager, next, sizes"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </slot>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
defineOptions({ name: 'AppTable' })

const props = defineProps({
  paginationConfig: {
    type: Object,
    default: () => {}
  },
  quickCreate: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['changePage', 'sizeChange', 'creatQuick'])

const pageSizes = [10, 20, 50, 100]
const quickInputRef = ref()

const showInput = ref(false)
const inputValue = ref('')

watch(showInput, (bool) => {
  if (!bool) {
    inputValue.value = ''
  }
})

function submitHandle() {
  emit('creatQuick', inputValue.value)
  showInput.value = false
}

function quickCreateHandel() {
  showInput.value = true
  nextTick(() => {
    quickInputRef.value?.focus()
  })
}

function handleSizeChange() {
  emit('sizeChange')
}
function handleCurrentChange() {
  emit('changePage')
}
defineExpose({})
</script>

<style lang="scss" scoped>
.app-table {
  &__pagination {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
