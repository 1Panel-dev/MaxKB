<template>
  <div class="upload-document p-12-24">
    <div class="flex align-center mb-16">
      <back-button to="-1" style="margin-left: -4px"></back-button>
      <h3 style="display: inline-block">{{ $t('views.document.uploadDocument') }}</h3>
    </div>
    <el-card style="--el-card-padding: 0">
      <div class="upload-document__main flex" v-loading="loading">
        <div class="upload-document__component main-calc-height">
          <el-scrollbar>
            <template v-if="active === 0">
              <div class="upload-component p-24">
                <!-- 上传文档 -->
                <UploadComponent ref="UploadComponentRef" />
              </div>
            </template>
            <template v-else-if="active === 1">
              <SetRules ref="SetRulesRef" />
            </template>
            <template v-else-if="active === 2">
              <ResultSuccess :data="successInfo" />
            </template>
          </el-scrollbar>
        </div>
      </div>
    </el-card>
    <div class="upload-document__footer text-right border-t" v-if="active !== 2">
      <el-button @click="router.go(-1)" :disabled="SetRulesRef?.loading || loading">{{
        $t('common.cancel')
      }}</el-button>
      <el-button @click="prev" v-if="active === 1" :disabled="SetRulesRef?.loading || loading">{{
        $t('views.document.buttons.prev')
      }}</el-button>
      <el-button
        @click="next"
        type="primary"
        v-if="active === 0"
        :disabled="SetRulesRef?.loading || loading"
      >
        {{
          documentsType === 'txt'
            ? $t('views.document.buttons.next')
            : $t('views.document.buttons.import')
        }}
      </el-button>
      <el-button
        @click="submit"
        type="primary"
        v-if="active === 1"
        :disabled="SetRulesRef?.loading || loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SetRules from './upload/SetRules.vue'
import ResultSuccess from './upload/ResultSuccess.vue'
import UploadComponent from './upload/UploadComponent.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
const { knowledge } = useStore()
const documentsFiles = computed(() => knowledge.documentsFiles)
const documentsType = computed(() => knowledge.documentsType)

const router = useRouter()
const route = useRoute()
const {
  params: { folderId },
  query: { id }, // id为knowledgeID，有id的是上传文档
} = route

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const SetRulesRef = ref()
const UploadComponentRef = ref()

const loading = ref(false)
const disabled = ref(false)
const active = ref(0)
const successInfo = ref<any>(null)
async function next() {
  disabled.value = true
  if (await UploadComponentRef.value.validate()) {
    if (documentsType.value === 'QA') {
      const fd = new FormData()
      documentsFiles.value.forEach((item: any) => {
        if (item?.raw) {
          fd.append('file', item?.raw)
        }
      })
      if (id) {
        // QA文档上传
        loadSharedApi({ type: 'document', systemType: apiType.value })
          .postQADocument(id as string, fd, loading)
          .then(() => {
            MsgSuccess(t('common.submitSuccess'))
            clearStore()
            router.push({
              path: `/knowledge/${id}/${folderId}/document`,
            })
          })
      }
    } else if (documentsType.value === 'table') {
      const fd = new FormData()
      documentsFiles.value.forEach((item: any) => {
        if (item?.raw) {
          fd.append('file', item?.raw)
        }
      })
      if (id) {
        // table文档上传
        loadSharedApi({ type: 'document', systemType: apiType.value })
          .postTableDocument(id as string, fd, loading)
          .then(() => {
            MsgSuccess(t('common.submitSuccess'))
            clearStore()
            router.push({
              path: `/knowledge/${id}/${folderId}/document`,
            })
          })
      }
    } else {
      if (active.value++ > 2) active.value = 0
    }
  } else {
    disabled.value = false
  }
}
const prev = () => {
  active.value = 0
}

function clearStore() {
  knowledge.saveDocumentsFile([])
  knowledge.saveDocumentsType('')
}
function submit() {
  loading.value = true
  const documents = [] as any
  SetRulesRef.value?.paragraphList.map((item: any) => {
    if (!SetRulesRef.value?.checkedConnect) {
      item.content.map((v: any) => {
        delete v['problem_list']
      })
    }
    documents.push({
      name: item.name,
      paragraphs: item.content,
      source_file_id: item.source_file_id,
    })
  })

  if (id) {
    // 上传文档
    loadSharedApi({ type: 'document', systemType: apiType.value })
      .putMulDocument(id as string, documents)
      .then(() => {
        MsgSuccess(t('common.submitSuccess'))
        clearStore()
        router.push({
          path: `/knowledge/${id}/${folderId}/document`,
        })
      })
      .catch(() => {
        loading.value = false
      })
  }
}
function back() {
  if (documentsFiles.value?.length > 0) {
    MsgConfirm(t('common.tip'), t('views.document.tip.saveMessage'), {
      confirmButtonText: t('common.confirm'),
      type: 'warning',
    })
      .then(() => {
        router.go(-1)
        clearStore()
      })
      .catch(() => {})
  } else {
    router.go(-1)
  }
}
onUnmounted(() => {
  clearStore()
})
</script>
<style lang="scss" scoped>
.upload-document {
  &__steps {
    min-width: 450px;
    max-width: 800px;
    width: 80%;
    margin: 0 auto;
    padding-right: 60px;

    :deep(.el-step__line) {
      left: 64% !important;
      right: -33% !important;
    }
  }

  &__component {
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
  }
  &__footer {
    padding: 16px 24px;
    position: fixed;
    bottom: 0;
    left: 0;
    background: #ffffff;
    width: 100%;
    box-sizing: border-box;
  }
  .upload-component {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
  }
}
</style>
