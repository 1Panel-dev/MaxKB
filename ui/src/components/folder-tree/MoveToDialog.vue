<template>
  <el-dialog
    :title="$t('common.moveTo')"
    v-model="dialogVisible"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    align-center
  >
    <folder-tree
      ref="treeRef"
      :source="source"
      :data="folderList"
      :default-expanded-keys="[currentNodeKey]"
      :canOperation="false"
      class="move-to-dialog-tree"
      @handleNodeClick="folderClickHandle"
    />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false" :loading="loading">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import folderApi from '@/api/folder'
import { MsgError, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
import { SourceTypeEnum } from '@/enums/common'
import KnowledgeApi from '@/api/knowledge/knowledge'
import ApplicationApi from '@/api/application/application'
import ToolApi from '@/api/tool/tool'
const { folder, application } = useStore()
const emit = defineEmits(['refresh'])

const props = defineProps({
  source: {
    type: String,
    default: '',
  },
})

const treeRef = ref()
const loading = ref(false)
const dialogVisible = ref(false)
const folderList = ref<any[]>([])
const detail = ref<any>({})
const selectForderId = ref<any>('')
const currentNodeKey = ref<string>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
    selectForderId.value = ''
    folderList.value = []
    currentNodeKey.value = ''
    treeRef.value?.clearCurrentKey()
  }
})

const isFolder = ref<boolean>(false)

const open = (data: any, is_folder?: any) => {
  detail.value = data
  isFolder.value = is_folder
  getFolder()
  dialogVisible.value = true
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder(props.source, params, loading).then((res: any) => {
    folderList.value = res.data
    if (folderList.value?.length > 0) {
      currentNodeKey.value = folderList.value[0]?.id
    } else {
      currentNodeKey.value = ''
    }
  })
}

function folderClickHandle(item: any) {
  selectForderId.value = item.id
}

const submitHandle = async () => {
  if (selectForderId.value) {
    const obj = {
      ...detail.value,
      folder_id: selectForderId.value,
    }
    if (isFolder.value) {
      const folder_obj = {
        ...detail.value,
        parent_id: selectForderId.value,
      }
      folderApi
        .putFolder(detail.value.id, detail.value.folder_type, folder_obj, loading)
        .then(() => {
          MsgSuccess(t('common.saveSuccess'))
          emit('refresh')
          dialogVisible.value = false
        })
    } else if (props.source === SourceTypeEnum.KNOWLEDGE) {
      if (detail.value.type === 2) {
        KnowledgeApi.putLarkKnowledge(detail.value.id, obj, loading).then(() => {
          MsgSuccess(t('common.saveSuccess'))
          emit('refresh', detail.value)
          dialogVisible.value = false
        })
      } else {
        KnowledgeApi.putKnowledge(detail.value.id, obj, loading).then(() => {
          MsgSuccess(t('common.saveSuccess'))
          emit('refresh', detail.value)
          dialogVisible.value = false
        })
      }
    } else if (props.source === SourceTypeEnum.TOOL) {
      ToolApi.putTool(detail.value.id, obj, loading).then(() => {
        MsgSuccess(t('common.saveSuccess'))
        emit('refresh', detail.value)
        dialogVisible.value = false
      })
    } else if (props.source === SourceTypeEnum.APPLICATION) {
      ApplicationApi.putApplication(detail.value.id, obj, loading).then((res) => {
        MsgSuccess(t('common.saveSuccess'))
        emit('refresh', detail.value)
        dialogVisible.value = false
      })
    }
  } else {
    MsgError(t('components.folder.requiredMessage'))
  }
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.move-to-dialog-tree {
  :deep(.el-input) {
    padding: 0 !important;
    margin-bottom: 8px;
  }
  :deep(.el-scrollbar) {
    border: 1px solid var(--el-border-color-light);
    border-radius: 6px;
  }
  :deep(.el-tree) {
    height: calc(100vh - 320px)!important;
  }
}
</style>
