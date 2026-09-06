<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormField } from '@/components/mk-dynamics-form'
import type { UserInputSetting } from '../../types'
import { exposedInputTypes } from './constant'

const props = defineProps<{ fields: FormField[] }>()
const emit = defineEmits<{ submit: [setting: UserInputSetting] }>()
const settingDialogVisible = ref(false)
const currentSetting = ref<UserInputSetting>({ exposed_fields: [], menu_title: '用户输入' })
const exposedFieldOptions = computed(() => props.fields.filter(({ input_type }) => exposedInputTypes.includes(input_type)))

function formatLabel(label: FormField['label'], fallback = '') {
  return typeof label === 'string' ? label : (label?.label ?? fallback)
}

function resetData() {
  currentSetting.value = { exposed_fields: [], menu_title: '用户输入' }
}

function open(setting: UserInputSetting) {
  resetData()
  currentSetting.value = cloneDeep(setting)
  settingDialogVisible.value = true
}

function submitSetting() {
  emit('submit', cloneDeep(currentSetting.value))
  settingDialogVisible.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="settingDialogVisible" title="设置" align-center @closed="resetData">
    <el-form :model="currentSetting" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item>
        <template #label>
          <span class="flex items-center gap-1">
            <span>外置参数设置（最多可显示3个）</span>
            <el-tooltip placement="right" content="仅支持模型、知识库、开关、日期、树形选项卡、单选框、多选框组件类型">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
        </template>
        <el-select v-model="currentSetting.exposed_fields" multiple :multiple-limit="3" placeholder="请选择">
          <el-option v-for="field in exposedFieldOptions" :key="field.field" :label="formatLabel(field.label, field.field)" :value="field.field" />
        </el-select>
      </el-form-item>
      <el-form-item label="其他参数收纳菜单标题" prop="menu_title" :rules="[{ required: true, message: '请输入', trigger: 'blur' }]">
        <el-input v-model="currentSetting.menu_title" maxlength="64" show-word-limit placeholder="请输入" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="settingDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitSetting">保存</el-button>
    </template>
  </MkDialog>
</template>
