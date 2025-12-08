<template>
  <el-form :model="form" ref="formRef" label-position="top" require-asterisk-position="right">
    <el-scrollbar>
      <div v-for="(element, index) in form" :key="index" class="flex w-full">
        <el-form-item
          v-for="model of props.models"
          :key="model.path"
          :prop="`[${index}].${model.path}`"
          :rules="model.rules"
          :label="index === 0 && model.label ? model.label : ''"
          class="mr-8"
          style="flex: 1"
        >
          <el-select
            v-if="!model?.hidden?.(element)"
            v-model="element[model.path]"
            :placeholder="model.selectProps?.placeholder ?? $t('common.selectPlaceholder')"
            :clearable="
              model.selectProps?.clearableFunction
                ? model.selectProps?.clearableFunction?.(element)
                : true
            "
            filterable
            multiple
            :reserve-keyword="false"
            style="width: 100%"
            collapse-tags
            collapse-tags-tooltip
            v-bind="model.selectProps"
          >
            <el-option
              v-for="opt in model.selectProps?.options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
              :disabled="selectedRoles.includes(opt.value)"
            >
              <el-tooltip effect="dark" :content="opt.label" placement="top" :show-after="500">
                <div class="ellipsis" style="max-width: 190px">{{ opt.label }}</div>
              </el-tooltip>
            </el-option>
          </el-select>
        </el-form-item>
        <!-- 删除按钮 -->
        <el-button
          :disabled="
            (props.keepOneLine && form.length === 1) || props.deleteButtonDisabled?.(element)
          "
          @click="handleDelete(index)"
          text
          :style="{
            'margin-top': index === 0 && props.models.some((item) => item.label) ? '32px' : '2px',
          }"
        >
          <AppIcon iconName="app-delete"></AppIcon>
        </el-button>
      </div>
    </el-scrollbar>
    <!-- 添加按钮 -->
    <el-button type="primary" text class="mt-2" @click="handleAdd">
      <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
      {{ props.addText ?? $t('views.role.member.add') }}
    </el-button>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { FormItemModel } from '@/api/type/role'

const props = defineProps<{
  models: FormItemModel[]
  addText?: string
  keepOneLine?: boolean // 至少保留一行
  deleteButtonDisabled?: (model: any) => boolean
}>()

const formRef = ref()
const formItem: Record<string, any> = {}
const form = defineModel<Record<string, any>[]>('form', {
  default: [],
})

const selectedRoles = computed(() => {
  return form.value.map((item) => item.role_id)
})

function handleAdd() {
  form.value.push({ ...formItem })
}

watch(
  () => props.models,
  () => {
    props.models.forEach((e) => {
      formItem[e.path] = []
    })
  },
  { immediate: true },
)

function handleDelete(index: number) {
  form.value.splice(index, 1)
}

const validate = () => {
  if (formRef.value) {
    return formRef.value?.validate()
  }
  return Promise.resolve()
}

const resetValidation = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}
defineExpose({ validate, resetValidation })
</script>
