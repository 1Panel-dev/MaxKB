<template>
  <el-dialog
    :title="$t('views.chatLog.selectKnowledge')"
    v-model="dialogVisible"
    width="600"
    class="select-knowledge-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <template #header="{ titleId, titleClass }">
      <h4 :id="titleId" :class="titleClass">{{ $t('views.chatLog.selectKnowledge') }}</h4>
    </template>

    <el-tree-select v-model="selectKnowledge" :data="knowledgeList" style="width: 240px">
      <template #default="{ data: { label } }">
        {{ label }}<span style="color: gray">(suffix)</span>
      </template>
    </el-tree-select>
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
  params: { id }, // id为knowledgeID
} = route as any

const emit = defineEmits(['refresh'])

const loading = ref<boolean>(false)

const dialogVisible = ref<boolean>(false)
const selectKnowledge = ref('')
const knowledgeList = ref<any>([])
const documentList = ref<any>([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    selectKnowledge.value = ''
    knowledgeList.value = []
    documentList.value = []
  }
})

const open = (list: any) => {
  documentList.value = list
  getKnowledge()
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

function getKnowledge() {
  knowledge.asyncGetRootKnowledge(loading).then((res: any) => {
    knowledgeList.value = res.data?.filter((v: any) => v.id !== id)
  })
}

const refresh = () => {
  getKnowledge()
}

defineExpose({ open })
</script>
<style lang="scss">
.select-knowledge-dialog {
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
