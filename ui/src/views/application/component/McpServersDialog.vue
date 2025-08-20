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
      hide-required-asterisk
      @submit.prevent
    >
      <el-form-item>
        <el-radio-group v-model="form.mcp_source" @change="mcpSourceChange">
          <el-radio value="referencing">
            {{ $t('views.applicationWorkflow.nodes.mcpNode.reference') }}
          </el-radio>
          <el-radio value="custom">{{ $t('common.custom') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        v-if="form.mcp_source === 'referencing'"
        :rules="[
          {
            required: true,
            message:
              $t('common.selectPlaceholder') +
              ` MCP ${$t('views.applicationWorkflow.nodes.mcpNode.tool')}`,
          },
        ]"
        prop="mcp_tool_id"
      >
        <template #label>
          {{ `MCP ${$t('views.applicationWorkflow.nodes.mcpNode.tool')}` }}
          <span class="color-danger">*</span>
        </template>
        <el-select v-model="form.mcp_tool_id" filterable>
          <el-option
            v-for="mcpTool in mcpToolSelectOptions"
            :key="mcpTool.id"
            :label="mcpTool.name"
            :value="mcpTool.id"
          >
            <div class="flex align-center">
              <el-avatar shape="square" :size="20" class="mr-8">
                <img src="@/assets/workflow/icon_mcp.svg" style="width: 75%" alt="" />
              </el-avatar>
              <span>{{ mcpTool.name }}</span>
              <el-tag v-if="mcpTool.scope === 'SHARED'" type="info" class="info-tag ml-8 mt-4">
                {{ $t('views.shared.title') }}
              </el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item
        v-else
        prop="mcp_servers"
        :rules="[
          {
            required: true,
            message: $t('common.inputPlaceholder') + ' ' + $t('views.tool.form.mcp.label'),
          },
        ]"
      >
        <template #label>
          {{ $t('views.tool.form.mcp.label') }}
          <span class="color-danger">*</span>
          <el-text type="info" class="color-secondary">
            （{{ $t('views.tool.form.mcp.tip') }}）
          </el-text>
        </template>
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
import { computed, inject, onMounted, ref, watch } from 'vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { useRoute } from 'vue-router'

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
  mcp_tool_id: '',
  mcp_source: 'referencing',
})

const mcpToolSelectOptions = ref<any[]>([])

const dialogVisible = ref<boolean>(false)

const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      mcp_servers: '',
      mcp_tool_id: '',
      mcp_source: 'referencing',
    }
    paramFormRef.value?.clearValidate()
  }
})

function mcpSourceChange() {
  if (form.value.mcp_source === 'referencing') {
    form.value.mcp_servers = ''
  } else {
    form.value.mcp_tool_id = ''
  }
}


const open = (data: any, selectOptions: any) => {
  form.value = { ...form.value, ...data }
  form.value.mcp_source = data.mcp_source || 'referencing'
  dialogVisible.value = true
  mcpToolSelectOptions.value = selectOptions || []
}

const submit = () => {
  paramFormRef.value.validate((valid: any) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
