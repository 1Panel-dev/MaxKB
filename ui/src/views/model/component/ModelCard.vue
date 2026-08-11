<template>
  <el-card shadow="hover" class="model-card" @mouseenter="hover = true" @mouseleave="hover = subHover">
    <div class="card-header">
      <div class="flex items-start gap-3">
        <div class="shrink-0">
          <span v-html="icon" class="inline-flex items-center justify-center shrink-0" style="width:20px;height:20px" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="font-semibold text-sm truncate" :title="model.name">{{ model.name }}</span>
            <el-tooltip v-if="currentModel.status === 'ERROR'" effect="dark" :content="errMessage" placement="top">
              <el-icon class="text-danger shrink-0" size="16"><WarningFilled /></el-icon>
            </el-tooltip>
          </div>
          <div class="text-xs text-gray-500 mt-1">
            <span :title="model.nick_name" class="truncate inline-block max-w-20">{{ model.nick_name }}</span>
            <span class="mx-1">创建于</span>
            <span>{{ formatDate(model.create_time) }}</span>
          </div>
        </div>
        <div class="shrink-0">
          <el-tag v-if="isShared || isSystemShare" size="small" type="info">共享</el-tag>
        </div>
      </div>
    </div>

    <div class="card-body mt-3">
      <div class="flex items-center gap-2 text-sm mb-1">
        <span class="text-gray-500 shrink-0">模型类型：</span>
        <span class="truncate">{{ modelTypeLabel }}</span>
      </div>
      <div class="flex items-center gap-2 text-sm">
        <span class="text-gray-500 shrink-0">基础模型：</span>
        <span class="truncate">{{ model.model_name || '--' }}</span>
      </div>
    </div>

    <div class="card-footer" v-if="!isShared">
      <el-dropdown trigger="click" @command="handleCommand">
        <el-button circle size="small" class="action-btn" @click.stop>
          <MkIcon :icon="MoreFilled" :size="16" />
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="edit" v-if="hasResourcePerm('model', 'edit')">
              <el-icon><Edit /></el-icon>
              编辑
            </el-dropdown-item>
            <el-dropdown-item command="paramSetting" v-if="hasParamSetting && hasResourcePerm('model', 'modelParam')">
              <el-icon><Operation /></el-icon>
              模型参数设置
            </el-dropdown-item>
            <el-dropdown-item command="auth" v-if="hasResourcePerm('model', 'auth')">
              <el-icon><Lock /></el-icon>
              资源授权
            </el-dropdown-item>
            <el-dropdown-item command="related" v-if="hasResourcePerm('model', 'relateMap')">
              <el-icon><Connection /></el-icon>
              查看关联资源
            </el-dropdown-item>
            <el-dropdown-item command="delete" divided v-if="hasResourcePerm('model', 'delete')">
              <el-icon><Delete /></el-icon>
              删除
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Model, Provider } from '@/api/type/model'
import modelApi from '@/api/model/model'
import { ElMessageBox, ElMessage } from 'element-plus'
import { WarningFilled, MoreFilled, Edit, Operation, Lock, Connection, Delete } from '@element-plus/icons-vue'
import { modelTypeList } from './data'
import { hasResourcePerm } from '@/composables/usePermission'

const props = withDefaults(
  defineProps<{
    model: Model
    providerList: Provider[]
    isShared?: boolean
    isSystemShare?: boolean
    apiType?: string
  }>(),
  {
    isShared: false,
    isSystemShare: false,
    apiType: 'workspace',
  },
)

const emit = defineEmits<{
  (e: 'change'): void
  (e: 'edit', model: Model): void
  (e: 'paramSetting', model: Model): void
}>()

const hover = ref(false)
const subHover = ref(false)

const icon = computed(() => {
  return props.providerList.find(p => p.provider === props.model.provider)?.icon || ''
})

const modelTypeLabel = computed(() => {
  const found = modelTypeList.find(mt => mt.value === props.model.model_type)
  return found ? found.text : props.model.model_type
})

const hasParamSetting = computed(() => {
  return ['TTS', 'STT', 'LLM', 'IMAGE', 'TTI', 'ITV', 'EMBEDDING', 'TTV'].includes(props.model.model_type)
})

const currentModel = computed(() => props.model)

const errMessage = computed(() => {
  if (props.model.meta?.message) {
    if (props.model.meta.message === 'pull model manifest: file does not exist') {
      return `${props.model.model_name} 模型不存在`
    }
    return props.model.meta.message
  }
  return ''
})

function formatDate(ts?: string) {
  if (!ts) return '--'
  const d = new Date(ts)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function handleCommand(cmd: string) {
  if (cmd === 'edit') {
    emit('edit', props.model)
  } else if (cmd === 'paramSetting') {
    emit('paramSetting', props.model)
  } else if (cmd === 'delete') {
    deleteModel()
  }
}

function deleteModel() {
  ElMessageBox.confirm(
    `确认删除「${props.model.name}」吗？${props.model.resource_count > 0 ? `该模型已关联 ${props.model.resource_count} 个资源` : ''}`,
    '提示',
    { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning', confirmButtonClass: 'danger' },
  ).then(() => {
    modelApi.deleteModel(props.model.id).then(() => {
      ElMessage.success('删除成功')
      emit('change')
    })
  }).catch(() => {})
}
</script>

<style lang="scss" scoped>
.model-card {
  position: relative;
  min-height: 140px;
  border-radius: 8px;
  transition: all 0.2s;
  &:hover {
    border-color: var(--mk-primary, var(--el-color-primary)) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .card-footer {
    position: absolute;
    right: 8px;
    bottom: 8px;
  }
  .action-btn {
    border: none;
    background: rgba(0,0,0,0.04);
    &:hover { background: rgba(0,0,0,0.1); }
  }
}
</style>
