<template>
  <el-dialog
    :title="$t('common.setting')"
    v-model="dialogVisible"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :destroy-on-close="true"
    :before-close="close"
    append-to-body
  >
    <el-form
      label-position="top"
      ref="fieldFormRef"
      :rules="rules"
      :model="form"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item>
        <template #label>
          <div class="flex align-center">
            <div class="mr-4">
              <span>{{ $t('aiChat.userInputSetting') }}</span>
            </div>
            <el-tooltip effect="dark" placement="right" popper-class="max-w-200">
              <template #content>{{ $t('aiChat.userInputSettingTip') }}</template>
              <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
            </el-tooltip>
          </div>
        </template>
        <el-select v-model="form.exposed_fields" multiple style="width: 100%">
          <el-option
            v-for="item in selectableFieldOptions"
            :key="item.field"
            :label="getFieldLabel(item)"
            :value="item.field"
            :disabled="form.exposed_fields.length >= 3 && !form.exposed_fields.includes(item.field)"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="$t('aiChat.remainingParamsMenuTitle')" prop="menu_title">
        <el-input
          v-model="form.menu_title"
          maxlength="64"
          show-word-limit
          @blur="form.menu_title = form.menu_title.trim()"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submit(fieldFormRef)" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import { t } from '@/locales'
import { ALLOWED_EXPOSED_TYPES } from '@/components/ai-chat/component/inline-params/constants'
const emit = defineEmits(['refresh'])

const fieldFormRef = ref()
const loading = ref<boolean>(false)
const fieldOptions = ref<any[]>([])

const selectableFieldOptions = computed(() =>
  fieldOptions.value.filter((item) => ALLOWED_EXPOSED_TYPES.includes(item.input_type)),
)

const form = ref<any>({
  exposed_fields: [],
  menu_title: t('common.moreSettings'),
})

const rules = reactive({
  menu_title: [{ required: true, message: t('common.inputPlaceholder'), trigger: 'blur' }],
})

const dialogVisible = ref<boolean>(false)

const getFieldLabel = (item: any) => {
  if (typeof item.label === 'string') return item.label
  if (item.label?.label) return item.label.label
  return item.field
}

const open = (row: any, fields?: any[], setting?: any, legacyTitle?: string) => {
  form.value = {
    exposed_fields: setting?.exposed_fields || [],
    menu_title: setting?.menu_title || legacyTitle || t('common.moreSettings'),
  }
  fieldOptions.value = fields || []
  dialogVisible.value = true
}

const close = () => {
  dialogVisible.value = false
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid) => {
    if (valid) {
      emit('refresh', {
        exposed_fields: form.value.exposed_fields,
        menu_title: form.value.menu_title,
      })
    }
  })
}

defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
