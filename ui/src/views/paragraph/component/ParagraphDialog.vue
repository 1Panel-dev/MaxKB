<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="80%"
    class="paragraph-dialog"
    destroy-on-close
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    append-to-body
  >
    <el-row v-loading="loading">
      <el-col :span="18">
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px">
            <div style="position: absolute; right: 20px; top: 20px">
              <el-button text @click="isEdit = true" v-if="paragraphId && !isEdit">
                <AppIcon iconName="app-edit"></AppIcon>
              </el-button>
            </div>

            <ParagraphForm
              ref="paragraphFormRef"
              :data="detail"
              :isEdit="isEdit"
              :knowledge-id="id"
            />
          </div>
        </el-scrollbar>
        <div class="text-right p-24 pt-0" v-if="paragraphId && isEdit">
          <el-button @click.prevent="cancelEdit"> {{ $t('common.cancel') }} </el-button>
          <el-button type="primary" :disabled="loading" @click="handleDebounceClick">
            {{ $t('common.save') }}
          </el-button>
        </div>
      </el-col>
      <el-col :span="6" class="border-l" style="width: 300px">
        <!-- 关联问题 -->
        <ProblemComponent
          v-if="permissionPrecise.problem_read(id)"
          :paragraphId="paragraphId"
          :docId="document_id"
          :knowledgeId="id"
          :apiType="apiType"
          ref="ProblemRef"
        />
      </el-col>
    </el-row>
    <template #footer v-if="!paragraphId">
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button :disabled="loading" type="primary" @click="handleDebounceClick">
          {{ $t('common.submit') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, debounce } from 'lodash'
import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'
import ProblemComponent from '@/views/paragraph/component/ProblemComponent.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import permissionMap from '@/permission'

const props = defineProps<{
  title: string
  apiType: 'systemShare' | 'workspace' | 'systemManage'
}>()

const route = useRoute()
const {
  params: { id, documentId },
} = route as any

const permissionPrecise = computed(() => {
  return permissionMap['knowledge'][props.apiType]
})

const emit = defineEmits(['refresh'])

const ProblemRef = ref()
const paragraphFormRef = ref<any>()

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const paragraphId = ref('')
const detail = ref<any>({})
const isEdit = ref(false)
const document_id = ref('')
const dataset_id = ref('')
const cloneData = ref(null)
const position = ref(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    paragraphId.value = ''
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

const open = (data: any, str: any) => {
  if (data && str === 'add') {
    isEdit.value = true
    position.value = data.position
  } else if (data) {
    detail.value.title = data.title
    detail.value.content = data.content
    cloneData.value = cloneDeep(detail.value)
    paragraphId.value = data.id
    document_id.value = data.document_id
    dataset_id.value = data.dataset_id || id
    if (str === 'edit') {
      isEdit.value = true
    } else {
      isEdit.value = false
    }
  } else {
    isEdit.value = true
  }
  dialogVisible.value = true
}
const submitHandle = async () => {
  if (await paragraphFormRef.value?.validate()) {
    loading.value = true
    if (paragraphId.value) {
      loadSharedApi({ type: 'paragraph', systemType: props.apiType })
        .putParagraph(
          dataset_id.value,
          documentId || document_id.value,
          paragraphId.value,
          paragraphFormRef.value?.form,
          loading,
        )
        .then((res: any) => {
          isEdit.value = false
          emit('refresh', res.data)
        })
    } else {
      const obj =
        ProblemRef.value.problemList.length > 0
          ? {
              position: String(position.value) ? position.value : null,
              problem_list: ProblemRef.value.problemList,
              ...paragraphFormRef.value?.form,
            }
          : {
              position: String(position.value) ? position.value : null,
              ...paragraphFormRef.value?.form,
            }
      loadSharedApi({ type: 'paragraph', systemType: props.apiType })
        .postParagraph(id, documentId, obj, loading)
        .then(() => {
          dialogVisible.value = false
          emit('refresh')
        })
    }
  }
}
const handleDebounceClick = debounce(() => {
  submitHandle()
}, 200)

defineExpose({ open, dialogVisible })
</script>
<style lang="scss" scoped></style>
