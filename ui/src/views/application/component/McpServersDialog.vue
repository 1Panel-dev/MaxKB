<template>
  <el-dialog
    align-center
    :title="$t('common.setting')"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      label-position="top"
      ref="paramFormRef"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item label="MCP" prop="mcp_enable">
        <el-switch v-model="form.mcp_enable" />
      </el-form-item>
      <el-form-item
        v-if="form.mcp_enable"
        :label="$t('views.applicationWorkflow.nodes.mcpNode.configLabel')"
        prop="mcp_servers"
        :rules="[{ required: true, message: $t('common.required') }]"
      >
        <el-input
          v-model="form.mcp_servers"
          :rows="6"
          type="textarea"
          :placeholder="mcpServerJson"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

const emit = defineEmits(['refresh'])

const paramFormRef = ref()

const mcpServerJson = `{
  "math": {
    "url": "your_server",
    "transport": "sse"
  }
}`

const form = ref<any>({
  mcp_servers: '',
  mcp_enable: false
})

const dialogVisible = ref<boolean>(false)
const loading = ref(false)
watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      mcp_servers: '',
      mcp_enable: false
    }
  }
})

const open = (data: any) => {
  form.value = { ...form.value, ...data }
  dialogVisible.value = true
}

const submit = () => {
  paramFormRef.value.validate().then((valid: any) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
