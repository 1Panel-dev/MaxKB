<template>
  <el-dialog
    align-center
    :title="$t('common.setting')"
    class="param-dialog"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form label-position="top" ref="paramFormRef" :model="form"
             require-asterisk-position="right">
      <el-form-item label="MCP" prop="mcp_enable">
        <el-switch v-model="form.mcp_enable" />
      </el-form-item>
      <el-form-item v-if="form.mcp_enable" label="MCP Server Config" prop="mcp_servers"
                    :rules="[{ required: true, message: $t('common.required') }]">
        <el-input
          v-model="form.mcp_servers"
          :rows="6"
          type="textarea"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer p-16">
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
<style lang="scss" scoped>
.param-dialog {
  padding: 8px 8px 24px 8px;

  .el-dialog__header {
    padding: 16px 16px 0 16px;
  }

  .el-dialog__body {
    padding: 0 !important;
  }

  .dialog-max-height {
    height: 560px;
  }

  .custom-slider {
    .el-input-number.is-without-controls .el-input__wrapper {
      padding: 0 !important;
    }
  }
}
</style>
