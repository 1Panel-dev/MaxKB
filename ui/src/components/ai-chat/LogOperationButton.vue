<template>
  <div>
    <el-text type="info">
      <span class="ml-4">{{ datetimeFormat(data.create_time) }}</span>
    </el-text>
  </div>
  <div>
    <el-tooltip effect="dark" content="复制" placement="top">
      <el-button text @click="copyClick(data?.answer_text)">
        <AppIcon iconName="app-copy"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip
      v-if="data.improve_paragraph_id_list.length === 0"
      effect="dark"
      content="修改内容"
      placement="top"
    >
      <el-button text @click="editContent(data)">
        <el-icon><EditPen /></el-icon>
      </el-button>
    </el-tooltip>

    <el-tooltip v-else effect="dark" content="修改标注" placement="top">
      <el-button text @click="editMark(data)">
        <AppIcon iconName="app-document-active" class="primary"></AppIcon>
      </el-button>
    </el-tooltip>

    <el-divider direction="vertical" v-if="buttonData?.vote_status !== '-1'" />
    <el-button text disabled v-if="buttonData?.vote_status === '0'">
      <AppIcon iconName="app-like-color"></AppIcon>
    </el-button>

    <el-button text disabled v-if="buttonData?.vote_status === '1'">
      <AppIcon iconName="app-oppose-color"></AppIcon>
    </el-button>
    <EditContentDialog ref="EditContentDialogRef" @refresh="refreshContent" />
    <EditMarkDialog ref="EditMarkDialogRef" @refresh="refreshMark" />
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditContentDialog from '@/views/log/component/EditContentDialog.vue'
import EditMarkDialog from '@/views/log/component/EditMarkDialog.vue'
import { datetimeFormat } from '@/utils/time'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  applicationId: {
    type: String,
    default: ''
  },
  log: Boolean
})

const emit = defineEmits(['update:data'])

const EditContentDialogRef = ref()
const EditMarkDialogRef = ref()

const buttonData = ref(props.data)

function editContent(data: any) {
  EditContentDialogRef.value.open(data)
}

function editMark(data: any) {
  EditMarkDialogRef.value.open(data)
}

function refreshMark() {
  buttonData.value.improve_paragraph_id_list = []
  emit('update:data', buttonData.value)
}
function refreshContent(data: any) {
  buttonData.value = data
  emit('update:data', buttonData.value)
}
</script>
<style lang="scss" scoped></style>
