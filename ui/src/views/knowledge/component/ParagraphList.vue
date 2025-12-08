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
              <AppIcon iconName="app-edit"></AppIcon>
            </el-button>
            <!-- 删除分段按钮  -->
            <el-button link @click="deleteHandle(child, cIndex)">
              <AppIcon iconName="app-delete"></AppIcon>
            </el-button>
          </div>
        </div>
        <div class="lighter mt-12">
          {{ child.content }}
        </div>
        <div class="lighter mt-12">
          <el-text type="info">
            {{ child.content.length }} {{ $t('views.paragraph.character_count') }}
          </el-text>
        </div>
      </el-card>
    </InfiniteScroll>

    <EditParagraphDialog
      ref="EditParagraphDialogRef"
      @updateContent="updateContent"
      :isConnect="isConnect"
      :knowledge-id="knowledgeId"
    />
  </div>
</template>
<script setup lang="ts">
import { cloneDeep } from 'lodash'
import { ref, computed, watchEffect } from 'vue'
import EditParagraphDialog from './EditParagraphDialog.vue'
import { MsgConfirm } from '@/utils/message'
import { t } from '@/locales'

const page_size = ref<number>(30)
const current_page = ref<number>(1)
const currentCIndex = ref<number>(0)
const EditParagraphDialogRef = ref()
const emit = defineEmits(['update:modelValue'])
const loading = ref<boolean>(false)
const localParagraphList = ref<any[]>([])

const props = defineProps({
  modelValue: {
    type: Array<any>,
    default: () => [],
  },
  isConnect: Boolean,
  knowledgeId: String,
})

// 初始化加载数据
watchEffect(() => {
  if (props.modelValue && props.modelValue.length > 0) {
    const end = page_size.value * current_page.value
    localParagraphList.value = props.modelValue.slice(0, Math.min(end, props.modelValue.length))
  }
})

// 监听分页变化，只加载需要的数据
watchEffect(() => {
  const start = 0
  const end = page_size.value * current_page.value
  // 不管数据量多少，都确保获取所有应该显示的数据
  localParagraphList.value = props.modelValue.slice(start, Math.min(end, props.modelValue.length))
})

const paragraph_list = computed(() => {
  return localParagraphList.value
})

const next = () => {
  if (loading.value) return
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 100)
}

const editHandle = (item: any, cIndex: number) => {
  // 计算实际索引，考虑分页
  currentCIndex.value = cIndex
  // currentCIndex.value = cIndex + page_size.value * (current_page.value - 1)
  // console.log('Edit index:', cIndex, page_size.value, current_page.value, currentCIndex.value)
  EditParagraphDialogRef.value.open(item)
}

const updateContent = (data: any) => {
  const new_value = [...props.modelValue]
  if (
    props.isConnect &&
    data.title &&
    !data?.problem_list.some((item: any) => item.content === data.title.trim())
  ) {
    data['problem_list'].push({
      content: data.title.trim(),
    })
  }
  new_value[currentCIndex.value] = cloneDeep(data)
  emit('update:modelValue', new_value)

  // 更新本地列表
  const localIndex = currentCIndex.value - page_size.value * (current_page.value - 1)
  if (localIndex >= 0 && localIndex < localParagraphList.value.length) {
    localParagraphList.value[localIndex] = cloneDeep(data)
  }
}

const deleteHandle = (item: any, cIndex: number) => {
  MsgConfirm(
    `${t('views.paragraph.delete.confirmTitle')}${item.title || '-'} ?`,
    t('views.paragraph.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      const new_value = [...props.modelValue]
      new_value.splice(cIndex, 1)
      emit('update:modelValue', new_value)

      // 更新本地列表
      localParagraphList.value.splice(cIndex, 1)
      // 如果当前页删除完了，从总数据中再取一条添加到末尾
      if (props.modelValue.length > localParagraphList.value.length * current_page.value) {
        const nextItem = props.modelValue[localParagraphList.value.length * current_page.value]
        if (nextItem) {
          localParagraphList.value.push(nextItem)
        }
      }
    })
    .catch(() => {})
}
</script>
<style lang="scss" scoped></style>
