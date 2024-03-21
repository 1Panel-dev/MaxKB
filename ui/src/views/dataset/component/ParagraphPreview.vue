<template>
  <el-tabs v-model="activeName" class="paragraph-tabs" @tab-click="handleClick">
    <template v-for="(item, index) in newData" :key="index">
      <el-tab-pane :label="item.name" :name="index">
        <template #label>
          <div class="flex-center">
            <img :src="getImgUrl(item && item?.name)" alt="" height="16" />
            <span class="ml-4">{{ item?.name }}</span>
          </div>
        </template>
        <el-scrollbar>
          <div class="mb-16">
            <el-text type="info">{{ item.content.length }} 段落</el-text>
          </div>

          <div class="paragraph-list">
            <el-card
              v-for="(child, cIndex) in item.content"
              :key="cIndex"
              shadow="never"
              class="card-never mb-16"
            >
              <div class="flex-between">
                <span>{{ child.title || '-' }}</span>
                <div>
                  <!-- 编辑分段按钮 -->
                  <el-button link @click="editHandle(child, index, cIndex)">
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                  <!-- 删除分段按钮  -->
                  <el-button link @click="deleteHandle(child, index, cIndex)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="lighter mt-12">
                {{ child.content }}
              </div>
              <div class="lighter mt-12">
                <el-text type="info"> {{ child.content.length }} 个字符 </el-text>
              </div>
            </el-card>
          </div>
        </el-scrollbar>
      </el-tab-pane>
    </template>
  </el-tabs>
  <EditParagraphDialog ref="EditParagraphDialogRef" @updateContent="updateContent" />
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { cloneDeep } from 'lodash'
import type { TabsPaneContext } from 'element-plus'
import EditParagraphDialog from './EditParagraphDialog.vue'
import { filesize, getImgUrl } from '@/utils/utils'
import { MsgConfirm } from '@/utils/message'

const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})

const emit = defineEmits(['update:data'])

const EditParagraphDialogRef = ref()

const activeName = ref(0)
const currentPIndex = ref(null) as any
const currentCIndex = ref(null) as any

const newData = ref<any[]>([])

watch(
  () => props.data,
  (value) => {
    newData.value = value
  },
  {
    immediate: true
  }
)

function editHandle(item: any, index: number, cIndex: number) {
  currentPIndex.value = index
  currentCIndex.value = cIndex
  EditParagraphDialogRef.value.open(item)
}

function deleteHandle(item: any, index: number, cIndex: number) {
  MsgConfirm(`是否删除分段：${item.title || '-'} ?`, `删除后将不会存入知识库，对本地文档无影响。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      newData.value[index].content.splice(cIndex, 1)
      emit('update:data', newData.value)
    })
    .catch(() => {})
}

function updateContent(data: any) {
  newData.value[currentPIndex.value].content[currentCIndex.value] = cloneDeep(data)
  emit('update:data', newData.value)
}

const handleClick = (tab: TabsPaneContext, event: Event) => {}

onMounted(() => {})
</script>
<style scoped lang="scss">
.paragraph-tabs {
  :deep(.el-tabs__item) {
    background: var(--app-text-color-light-1);
    margin: 4px;
    border-radius: 4px;
    padding: 5px 10px 5px 8px !important;
    height: auto;
    &:nth-child(2) {
      margin-left: 0;
    }
    &:last-child {
      margin-right: 0;
    }
    &.is-active {
      border: 1px solid var(--el-color-primary);
      background: var(--el-color-primary-light-9);
      color: var(--el-text-color-primary);
    }
  }
  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }
  :deep(.el-tabs__active-bar) {
    display: none;
  }
}
.paragraph-list {
  height: calc(var(--create-dataset-height) - 131px);
}
</style>
