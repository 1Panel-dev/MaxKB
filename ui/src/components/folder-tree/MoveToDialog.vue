<template>
  <el-dialog
    :title="$t('common.moveTo')"
    v-model="dialogVisible"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <folder-tree
      :source="source"
      :data="folderList"
      :treeStyle="{
        height: 'auto',
        border: '1px solid #ebeef5',
        borderRadius: '6px',
        padding: '8px',
      }"
      :default-expanded-keys="['default']"
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
import { MsgError, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
import { SourceTypeEnum } from '@/enums/common'
import KnowledgeApi from '@/api/knowledge/knowledge'
import ToolApi from '@/api/tool/tool'
const { folder, application } = useStore()
const emit = defineEmits(['refresh'])

const props = defineProps({
  source: {
    type: String,
    default: '',
  },
})

const loading = ref(false)
const dialogVisible = ref(false)
const folderList = ref<any[]>([])
const detail = ref<any>({})
const selectForderId = ref<any>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
    selectForderId.value = ''
    folderList.value = []
  }
})

const open = (data: any) => {
  detail.value = data
  getFolder()
  dialogVisible.value = true
}

function getFolder() {
  const params = {}
  folder.asyncGetFolder(props.source, params, loading).then((res: any) => {
    folderList.value = res.data
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
    if (props.source === SourceTypeEnum.KNOWLEDGE) {
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
      application.asyncPutApplication(detail.value.id, obj, loading).then((res) => {
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
}
</style>
