<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="800"
    class="paragraph-dialog"
    destroy-on-close
  >
    <el-row>
      <el-col :span="16" class="p-24">
        <div class="flex-between mb-16">
          <div class="bold title align-center">分段内容</div>
          <el-button text v-if="pId">
            <el-icon><EditPen /></el-icon>
          </el-button>
        </div>

        <ParagraphForm ref="paragraphFormRef" :data="detail" />
        <div class="text-right">
          <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
          <el-button type="primary" :disabled="loading" @click="submitHandle"> 保存 </el-button>
        </div>
      </el-col>
      <el-col :span="8" class="border-l p-24">
        <p class="bold title mb-16">
          关联问题 <el-divider direction="vertical" />
          <el-button text>
            <el-icon><Plus /></el-icon>
          </el-button>
        </p>
        <el-input
          v-model="questionValue"
          @change="addQuestion"
          placeholder="请输入问题，回车保存"
          class="mb-8"
        />
        <template v-for="(item, index) in questionList" :key="index">
          <TagEllipsis class="question-tag" type="info" effect="plain" closable>
            {{ item.content }}
          </TagEllipsis>
        </template>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'
import datasetApi from '@/api/dataset'
import useStore from '@/stores'

const props = defineProps({
  title: String
})

const { paragraph } = useStore()

const route = useRoute()
const {
  params: { datasetId, documentId }
} = route as any

const emit = defineEmits(['refresh'])

const paragraphFormRef = ref<FormInstance>()

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const pId = ref('')
const detail = ref<any>({})
const isEdit = ref(false)

const questionValue = ref('')
const questionList = ref<any[]>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    pId.value = ''
    detail.value = {}
    isEdit.value = false
  }
})

function addQuestion() {}

const open = (data: any) => {
  if (data) {
    detail.value.title = data.title
    detail.value.content = data.content
    pId.value = data.id
    isEdit.value = true
  }
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    loading.value = true
    if (id) {
      paragraph
        .asyncPutParagraph(datasetId, documentId, pId, paragraphFormRef.value?.form)
        .then((res) => {
          emit('refresh')
          loading.value = false
          dialogVisible.value = false
        })
        .catch(() => {
          loading.value = false
        })
    } else {
      datasetApi
        .postParagraph(datasetId, documentId, paragraphFormRef.value?.form)
        .then((res) => {
          emit('refresh')
          loading.value = false
          dialogVisible.value = false
        })
        .catch(() => {
          loading.value = false
        })
    }
  }
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.paragraph-dialog {
  .el-dialog__header {
    padding-bottom: 16px;
  }
  .el-dialog__body {
    border-top: 1px solid var(--el-border-color);
    padding: 0 !important;
  }
  .title {
    color: var(--app-text-color);
  }
  .question-tag {
    width: 217px;
  }
}
</style>
