<template>
  <div>
    <el-text type="info">
      消耗: {{ data?.message_tokens + data?.answer_tokens }} tokens
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
    <el-tooltip effect="dark" content="修改内容" placement="top">
      <el-button text @click="editContent(data)">
        <el-icon><EditPen /></el-icon>
      </el-button>
    </el-tooltip>

    <!-- <el-divider direction="vertical" />
    <el-tooltip placement="bottom-start" effect="dark" content="修改内容">
      <el-popover :width="580" trigger="click">
        <template #reference>
          <el-button text>
            <el-icon><Document /></el-icon>
          </el-button>
        </template>
        <h4>修改内容</h4>
        <el-input
          v-model="data.content"
          placeholder="请输入内容"
          maxlength="1024"
          show-word-limit
          :rows="8"
          type="textarea"
        >
        </el-input>
      </el-popover>
    </el-tooltip> -->
    <el-divider direction="vertical" v-if="buttonData?.vote_status !== '-1'" />
    <el-button text disabled>
      <AppIcon iconName="app-like-color"></AppIcon>
    </el-button>

    <el-button text disabled v-if="buttonData?.vote_status === '1'">
      <AppIcon iconName="app-oppose-color"></AppIcon>
    </el-button>
    <EditContentDialog ref="EditContentDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { copyClick } from '@/utils/clipboard'
import EditContentDialog from '@/views/log/component/EditContentDialog.vue'
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

const buttonData = ref(props.data)
const loading = ref(false)

function editContent(data: any) {
  EditContentDialogRef.value.open(data)
}

// function updateContent(data: any) {
//   emit('update:data', data)
// }
</script>
<style lang="scss" scoped></style>
