<template>
  <div class="chat-knowledge-source">
    <div
      class="flex align-center mt-16"
      v-if="type === 'log' || type === 'debug-ai-chat' ? true : application.show_source"
    >
      <span class="mr-4 color-secondary">{{ $t('chat.KnowledgeSource.title') }}</span>
      <el-divider direction="vertical" />
      <el-button type="primary" class="mr-8" link @click="openParagraph(data)">
        <AppIcon iconName="app-reference-outlined" class="mr-4"></AppIcon>
        {{ $t('chat.KnowledgeSource.referenceParagraph') }}
        {{ data.paragraph_list?.length || 0 }}</el-button
      >
    </div>

    <div
      class="mt-8"
      v-if="type === 'log' || type === 'debug-ai-chat' ? true : application.show_source"
    >
      <el-row :gutter="8" v-if="uniqueParagraphList?.length">
        <template v-for="(item, index) in uniqueParagraphList" :key="index">
          <el-col :span="12" class="mb-8">
            <el-card shadow="never" style="--el-card-padding: 8px">
              <div class="flex-between">
                <div class="flex align-center">
                  <img
                    src="@/assets/fileType/web-link-icon.svg"
                    alt=""
                    width="24"
                    v-if="item?.meta?.source_file_id || item?.meta?.source_url"
                  />
                  <img v-else :src="getImgUrl(item && item?.document_name)" alt="" width="24" />
                  <div
                    class="ml-4 ellipsis-1"
                    :title="item?.document_name"
                    v-if="showPDF(item)"
                    @click="openParagraphDocument(item)"
                  >
                    <p>{{ item && item?.document_name }}</p>
                  </div>
                  <div
                    class="ml-4"
                    v-else-if="item?.meta?.source_file_id || item?.meta?.source_url"
                  >
                    <a
                      :href="getFileUrl(item?.meta?.source_file_id) || item?.meta?.source_url"
                      target="_blank"
                      class="ellipsis-1"
                      :title="item?.document_name?.trim()"
                    >
                      <span :title="item?.document_name?.trim()">{{ item?.document_name }}</span>
                    </a>
                  </div>
                  <div v-else @click="infoMessage(item)">
                    <span class="ellipsis-1 break-all" :title="item?.document_name?.trim()">
                      {{ item?.document_name?.trim() }}
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </template>
      </el-row>
    </div>

    <div
      v-if="type === 'log' || type === 'debug-ai-chat' ? true : application.show_exec"
      class="execution-details border-t color-secondary flex-between mt-12"
      style="padding-top: 12px; padding-bottom: 8px"
    >
      <div>
        <span class="mr-8">
          {{ $t('chat.KnowledgeSource.consume') }}: {{ data?.message_tokens + data?.answer_tokens }}
        </span>
        <span>
          {{ $t('chat.KnowledgeSource.consumeTime') }}: {{ data?.run_time?.toFixed(2) }} s</span
        >
      </div>
      <el-button
        type="primary"
        link
        @click="openExecutionDetail(data.execution_details)"
        style="padding: 0"
      >
        <el-icon class="mr-4"><Document /></el-icon>
        {{ $t('chat.executionDetails.title') }}</el-button
      >
    </div>
    <!-- 知识库引用/执行详情 dialog -->
    <el-dialog
      class="scrollbar-dialog"
      :title="dialogTitle"
      v-model="dialogVisible"
      destroy-on-close
      append-to-body
      align-center
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <template #header="{ titleId, titleClass }">
        <div class="flex-between">
          <span class="medium ellipsis" :title="dialogTitle" :id="titleId" :class="titleClass">
            {{ dialogTitle }}
          </span>
          <!-- <div class="flex align-center mr-8" v-if="dialogType === 'pdfDocument'">
            <span class="mr-4">
              <el-button text>
                <el-icon> <Download /> </el-icon>
              </el-button>
            </span>
            <span>
              <el-button text> <app-icon iconName="app-export" size="20" /></el-button>
            </span>
            <el-divider direction="vertical" />
          </div> -->
        </div>
      </template>

      <el-scrollbar>
        <div class="mb-8 p-8" style="max-height: calc(100vh - 260px)">
          <component
            :is="currentComponent"
            :detail="currentChatDetail"
            :appType="appType"
          ></component>
        </div>
      </el-scrollbar>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, shallowRef } from 'vue'
import { cloneDeep } from 'lodash'
import ExecutionDetailContent from './ExecutionDetailContent.vue'
import ParagraphDocumentContent from './ParagraphDocumentContent.vue'
import ParagraphSourceContent from './ParagraphSourceContent.vue'
import { arraySort } from '@/utils/array'
import { getImgUrl, getFileUrl } from '@/utils/common'
import { t } from '@/locales'
import { MsgInfo } from '@/utils/message'
const props = defineProps({
  data: {
    type: Object,
    default: () => {},
  },
  type: {
    type: String,
    default: '',
  },
  appType: {
    type: String,
    default: '',
  },
  executionIsRightPanel: {
    type: Boolean,
    required: false,
  },
  application: {
    type: Object,
    default: () => {},
  },
})

const emit = defineEmits(['openExecutionDetail', 'openParagraph', 'openParagraphDocument'])
const showPDF = (item: any) => {
  return (
    item.document_name.toLocaleLowerCase().endsWith('.pdf') &&
    item.meta?.source_file_id &&
    props.executionIsRightPanel
  )
}
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentComponent = shallowRef<any>(null)
const currentChatDetail = ref<any>(null)
const dialogType = ref('')

function infoMessage(data: any) {
  if (data?.meta?.allow_download === false) {
    MsgInfo(t('chat.noPermissionDownload'))
  } else {
    MsgInfo(t('chat.noDocument'))
  }
}
function openParagraph(row: any, id?: string) {
  dialogTitle.value = t('chat.KnowledgeSource.title')
  const obj = cloneDeep(row)
  obj.paragraph_list = id
    ? obj.paragraph_list.filter((v: any) => v.knowledge_id === id)
    : obj.paragraph_list
  obj.paragraph_list = arraySort(obj.paragraph_list, 'similarity', true)
  if (props.executionIsRightPanel) {
    emit('openParagraph')
    return
  }
  dialogType.value = ''
  currentComponent.value = ParagraphSourceContent
  currentChatDetail.value = obj
  dialogVisible.value = true
}
function openExecutionDetail(row: any) {
  dialogTitle.value = t('chat.executionDetails.title')
  if (props.executionIsRightPanel) {
    emit('openExecutionDetail')
    return
  }
  dialogType.value = ''
  currentComponent.value = ExecutionDetailContent
  currentChatDetail.value = row
  dialogVisible.value = true
}
function openParagraphDocument(row: any) {
  if (props.executionIsRightPanel) {
    emit('openParagraphDocument', row)
    return
  }
  dialogType.value = 'pdfDocument'
  currentComponent.value = ParagraphDocumentContent
  dialogTitle.value = row.document_name
  currentChatDetail.value = row
  dialogVisible.value = true
}

const uniqueParagraphList = computed(() => {
  const seen = new Set()
  return (
    props.data.paragraph_list?.filter((paragraph: any) => {
      const key = paragraph.document_name.trim()
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      // 判断如果 meta 属性不是 {} 需要json解析 转对象
      if (paragraph.meta && typeof paragraph.meta === 'string') {
        paragraph.meta = JSON.parse(paragraph.meta)
        paragraph.source_url = paragraph.meta.source_url
      }
      return true
    }) || []
  )
})
</script>
<style lang="scss" scoped>
@media only screen and (max-width: 420px) {
  .chat-knowledge-source {
    .execution-details {
      display: block;
    }
  }
}
</style>
