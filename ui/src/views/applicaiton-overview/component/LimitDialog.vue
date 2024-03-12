<template>
  <el-dialog title="访问限制" v-model="dialogVisible">
    <el-form label-position="top" ref="limitFormRef" :model="form">
      <el-form-item label="文档地址" prop="source_url">
        <el-input-number
          v-model="form.min_star"
          :min="0"
          :step="1"
          controls-position="right"
          step-strictly
        />
        次 / 天
      </el-form-item>
      <el-form-item label="白名单" @click.prevent>
        <el-switch size="small" v-model="form.multiple_rounds_dialogue"></el-switch>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="form.source_url"
          placeholder="请输入域名或IP地址，一行一个。"
          :rows="10"
          type="textarea"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> 取消 </el-button>
        <el-button type="primary" @click="submit(limitFormRef)" :loading="loading">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { copyClick } from '@/utils/clipboard'
import overviewApi from '@/api/application-overview'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
const route = useRoute()
const {
  params: { id }
} = route
const { application } = useStore()

const emit = defineEmits(['addData'])

const limitFormRef = ref()
const form = ref<any>({
  type: '0',
  source_url: '',
  selector: ''
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      type: '0',
      source_url: '',
      selector: ''
    }
  }
})

const open = () => {
  dialogVisible.value = true
}

function submit() {}

defineExpose({ open })
</script>
<style lang="scss" scope>
.embed-dialog {
  .code {
    color: var(--app-text-color) !important;
    background: var(--app-layout-bg-color);
    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 180px;
  }
}
</style>
