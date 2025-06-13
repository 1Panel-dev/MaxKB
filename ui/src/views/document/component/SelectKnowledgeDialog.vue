<template>
  <el-dialog
    :title="$t('views.chatLog.selectKnowledge')"
    v-model="dialogVisible"
    width="600"
    class="select-dataset-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <div class="my-header flex">
        <h4 :id="titleId" :class="titleClass">{{ $t('views.chatLog.selectKnowledge') }}</h4>
        <el-button link class="ml-16" @click="refresh">
          <el-icon class="mr-4"><Refresh /></el-icon>{{ $t('common.refresh') }}
        </el-button>
      </div>
    </template>
    <div class="content-height">
      <el-radio-group v-model="selectKnowledge" class="card__radio">
        <el-scrollbar height="500">
          <div class="p-16">
            <el-row :gutter="12" v-loading="loading">
              <el-col :span="12" v-for="(item, index) in datasetList" :key="index" class="mb-16">
                <el-card shadow="never" :class="item.id === selectKnowledge ? 'active' : ''">
                  <el-radio :value="item.id" size="large">
                    <div class="flex align-center">
                      <KnowledgeIcon :type="item.type" />

                      <span class="ellipsis" :title="item.name">
                        {{ item.name }}
                      </span>
                    </div>
                  </el-radio>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </el-radio-group>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitHandle" :disabled="!selectKnowledge || loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/knowledge/document'

import useStore from '@/stores'
const { knowledge } = useStore()
const route = useRoute()
const {
  params: { id }, // id为datasetID
} = route as any

const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)

const dialogVisible = ref<boolean>(false)
const selectKnowledge = ref('')
const datasetList = ref<any>([])
const documentList = ref<any>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    selectKnowledge.value = ''
    datasetList.value = []
    documentList.value = []
  }
})

const open = (list: any) => {
  documentList.value = list
  getDataset()
  dialogVisible.value = true
}
const submitHandle = () => {
  documentApi
    .putMigrateMulDocument(id, selectKnowledge.value, documentList.value, loading)
    .then((res) => {
      emit('refresh')
      dialogVisible.value = false
    })
}

function getDataset() {
  knowledge.asyncGetRootKnowledge(loading).then((res: any) => {
    datasetList.value = res.data?.filter((v: any) => v.id !== id)
  })
}

const refresh = () => {
  getDataset()
}

defineExpose({ open })
</script>
<style lang="scss">
.select-dataset-dialog {
  padding: 0;
  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .el-dialog__footer {
    padding: 0 24px 24px;
  }
}
</style>
