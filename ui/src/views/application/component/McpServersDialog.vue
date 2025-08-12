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
      <el-form-item>
        <el-radio-group v-model="form.mcp_source">
          <el-radio value="referencing">
            {{ $t('views.applicationWorkflow.nodes.mcpNode.reference') }}
          </el-radio>
          <el-radio value="custom">{{ $t('common.custom') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="form.mcp_source === 'referencing'">
        <el-select v-model="form.mcp_tool_id" filterable>
          <el-option
            v-for="mcpTool in mcpToolSelectOptions"
            :key="mcpTool.id"
            :label="mcpTool.name"
            :value="mcpTool.id"
          >
            <span>{{ mcpTool.name }}</span>
            <el-tag v-if="mcpTool.scope === 'SHARED'" type="info" class="info-tag ml-8 mt-4">
              {{ $t('views.shared.title') }}
            </el-tag>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item
        v-else
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
import {computed, inject, onMounted, ref, watch} from 'vue'
import {loadSharedApi} from "@/utils/dynamics-api/shared-api.ts";
import {useRoute} from "vue-router";

const getApplicationDetail = inject('getApplicationDetail') as any
const applicationDetail = getApplicationDetail()
const emit = defineEmits(['refresh'])
const route = useRoute()
const apiType = computed(() => {
  if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})
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
  }
})


function getMcpToolSelectOptions() {
  const obj =
    apiType.value === 'systemManage'
      ? {
        scope: 'WORKSPACE',
        tool_type: 'MCP',
        workspace_id: applicationDetail.value?.workspace_id,
      }
      : {
        scope: 'WORKSPACE',
        tool_type: 'MCP',
      }

  loadSharedApi({type: 'tool', systemType: apiType.value})
    .getAllToolList(obj, loading)
    .then((res: any) => {
      mcpToolSelectOptions.value = [...res.data.shared_tools, ...res.data.tools]
        .filter((item: any) => item.is_active)
    })
}

const open = (data: any) => {
  form.value = {...form.value, ...data}
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

onMounted(() => {
  getMcpToolSelectOptions()
})

defineExpose({open})
</script>
<style lang="scss" scoped></style>
