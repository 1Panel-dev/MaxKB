<template>
  <div class="app-table" :class="quickCreate ? 'table-quick-append' : ''">
    <el-table :max-height="tableHeight" v-bind="$attrs">
      <template #append v-if="quickCreate">
        <div v-if="showInput">
          <el-input
            ref="quickInputRef"
            v-model="inputValue"
            :placeholder="`请输入${quickCreateName}`"
            class="w-500 mr-12"
            autofocus
            :maxlength="quickCreateMaxlength || '-'"
            :show-word-limit="quickCreateMaxlength ? true : false"
            @keydown.enter="submitHandle"
          />

          <el-button type="primary" @click="submitHandle" :disabled="loading">创建</el-button>
          <el-button @click="showInput = false" :disabled="loading">取消</el-button>
        </div>
        <div v-else @click="quickCreateHandel" class="w-full">
          <el-button type="primary" link class="quich-button">
            <el-icon><Plus /></el-icon>
            <span class="ml-4">{{ quickCreatePlaceholder }}</span>
          </el-button>
        </div>
      </template>
      <slot></slot>
    </el-table>
    <div class="app-table__pagination mt-16" v-if="$slots.pagination || paginationConfig">
      <slot name="pagination">
        <el-pagination
          v-model:current-page="paginationConfig.current_page"
          v-model:page-size="paginationConfig.page_size"
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
import { ref, nextTick, watch, computed, onMounted } from 'vue'
import { MsgError } from '@/utils/message'
defineOptions({ name: 'AppTable' })

import useStore from '@/stores'
const { common } = useStore()

const props = defineProps({
  paginationConfig: {
    type: Object,
    default: () => {}
  },
  quickCreate: {
    type: Boolean,
    default: false
  },
  quickCreateName: {
    type: String,
    default: '文档名称'
  },
  quickCreatePlaceholder: {
    type: String,
    default: '快速创建空白文档'
  },
  quickCreateMaxlength: {
    type: Number,
    default: () => 0
  },
  storeKey: String
})
const emit = defineEmits(['changePage', 'sizeChange', 'creatQuick'])

const paginationConfig = computed(() => props.paginationConfig)

const pageSizes = [10, 20, 50, 100]

const quickInputRef = ref()

const loading = ref(false)
const showInput = ref(false)
const inputValue = ref('')
const tableHeight = ref(0)

watch(showInput, (bool) => {
  if (!bool) {
    inputValue.value = ''
  }
})

function submitHandle() {
  if (inputValue.value) {
    loading.value = true
    emit('creatQuick', inputValue.value)
    setTimeout(() => {
      showInput.value = false
      loading.value = false
    }, 200)
  } else {
    MsgError(`${props.quickCreateName}不能为空！`)
  }
}

function quickCreateHandel() {
  showInput.value = true
  nextTick(() => {
    quickInputRef.value?.focus()
  })
}

function handleSizeChange() {
  emit('sizeChange')
  if (props.storeKey) {
    common.savePage(props.storeKey, props.paginationConfig)
  }
}
function handleCurrentChange() {
  emit('changePage')
  if (props.storeKey) {
    common.savePage(props.storeKey, props.paginationConfig)
  }
}
defineExpose({})

onMounted(() => {
  tableHeight.value = window.innerHeight - 300
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 300
    })()
  }
})
</script>

<style lang="scss" scoped>
.app-table {
  &__pagination {
    display: flex;
    justify-content: flex-end;
  }
  .quich-button {
    &:hover {
      color: var(--el-button-text-color);
    }
  }
}
</style>
