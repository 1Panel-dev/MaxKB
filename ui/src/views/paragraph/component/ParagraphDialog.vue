<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="80%"
    class="paragraph-dialog"
    destroy-on-close
  >
    <el-row v-loading="loading">
      <el-col :span="18">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px">
            <div class="flex-between mb-16">
              <div class="bold title align-center">分段内容</div>
              <el-button text @click="isEdit = true" v-if="problemId && !isEdit">
                <el-icon><EditPen /></el-icon>
              </el-button>
            </div>

            <ParagraphForm ref="paragraphFormRef" :data="detail" :isEdit="isEdit" />
          </div>
        </el-scrollbar>
        <div class="text-right p-24 pt-0" v-if="problemId && isEdit">
          <el-button @click.prevent="cancelEdit"> 取消 </el-button>
          <el-button type="primary" :disabled="loading" @click="handleDebounceClick">
            保存
          </el-button>
        </div>
      </el-col>
      <el-col :span="6" class="border-l" style="width: 300px;">
        <!-- 关联问题 -->
        <ProblemComponent
          :problemId="problemId"
          :docId="document_id"
          :datasetId="dataset_id"
          ref="ProblemRef"
        />
      </el-col>
    </el-row>
    <template #footer v-if="!problemId">
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button :disabled="loading" type="primary" @click="handleDebounceClick">
          提交
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, debounce } from 'lodash'

import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'
import ProblemComponent from '@/views/paragraph/component/ProblemComponent.vue'
import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'

const props = defineProps({
  title: String
})

const { paragraph } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])

const ProblemRef = ref()
const paragraphFormRef = ref<any>()

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const problemId = ref('')
const detail = ref<any>({})
const isEdit = ref(false)
const document_id = ref('')
const dataset_id = ref('')
const cloneData = ref(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    problemId.value = ''
    detail.value = {}
    isEdit.value = false
    document_id.value = ''
    dataset_id.value = ''
    cloneData.value = null
  }
})

const cancelEdit = () => {
  isEdit.value = false
  detail.value = cloneDeep(cloneData.value)
}

const open = (data: any) => {
  if (data) {
    detail.value.title = data.title
    detail.value.content = data.content
    cloneData.value = cloneDeep(detail.value)
    problemId.value = data.id
    document_id.value = data.document_id
    dataset_id.value = data.dataset_id || id
  } else {
    isEdit.value = true
  }
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    loading.value = true
    if (problemId.value) {
      paragraph
        .asyncPutParagraph(
          dataset_id.value,
          documentId || document_id.value,
          problemId.value,
          paragraphFormRef.value?.form,
          loading
        )
        .then((res: any) => {
          isEdit.value = false
          emit('refresh', res.data)
        })
    } else {
      const obj =
        ProblemRef.value.problemList.length > 0
          ? {
              problem_list: ProblemRef.value.problemList,
              ...paragraphFormRef.value?.form
            }
          : paragraphFormRef.value?.form
      paragraphApi.postParagraph(id, documentId, obj, loading).then((res) => {
        dialogVisible.value = false
        emit('refresh')
      })
    }
  }
}
const handleDebounceClick = debounce(() => {
  submitHandle()
}, 200)

defineExpose({ open })
</script>
<style lang="scss" scope>

</style>
