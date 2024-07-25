<template>
  <div>
    <InfiniteScroll
      :size="paragraph_list.length"
      :total="modelValue.length"
      :page_size="page_size"
      v-model:current_page="current_page"
      @load="next()"
      :loading="loading"
    >
      <el-card
        v-for="(child, cIndex) in paragraph_list"
        :key="cIndex"
        shadow="never"
        class="card-never mb-16"
      >
        <div class="flex-between">
          <span>{{ child.title || '-' }}</span>
          <div>
            <!-- 编辑分段按钮 -->
            <el-button link @click="editHandle(child, cIndex)">
              <el-icon><EditPen /></el-icon>
            </el-button>
            <!-- 删除分段按钮  -->
            <el-button link @click="deleteHandle(child, cIndex)">
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
    </InfiniteScroll>

    <EditParagraphDialog
      ref="EditParagraphDialogRef"
      @updateContent="updateContent"
      :isConnect="isConnect"
    />
  </div>
</template>
<script setup lang="ts">
import { cloneDeep } from 'lodash'
import { ref, computed } from 'vue'
import EditParagraphDialog from './EditParagraphDialog.vue'
import { MsgConfirm } from '@/utils/message'
const page_size = ref<number>(20)
const current_page = ref<number>(1)
const currentCIndex = ref<number>(0)
const EditParagraphDialogRef = ref()
const emit = defineEmits(['update:modelValue'])
const loading = ref<boolean>(false)
const editHandle = (item: any, cIndex: number) => {
  currentCIndex.value = cIndex
  EditParagraphDialogRef.value.open(item)
}

const props = defineProps<{ modelValue: Array<any>; isConnect: boolean }>()

const paragraph_list = computed(() => {
  return props.modelValue.slice(0, page_size.value * (current_page.value - 1) + page_size.value)
})

const next = () => {
  loading.value = true
  current_page.value += 1
  loading.value = false
}

const updateContent = (data: any) => {
  const new_value = [...props.modelValue]
  new_value[currentCIndex.value] = cloneDeep(data)
  emit('update:modelValue', new_value)
}

const deleteHandle = (item: any, cIndex: number) => {
  MsgConfirm(`是否删除分段：${item.title || '-'} ?`, `删除后将不会存入知识库，对本地文档无影响。`, {
    confirmButtonText: '删除',
    confirmButtonClass: 'danger'
  })
    .then(() => {
      const new_value = [...props.modelValue]
      new_value.splice(cIndex, 1)
      emit('update:modelValue', new_value)
    })
    .catch(() => {})
}
</script>
<style lang="scss" scoped></style>
