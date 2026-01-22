<template>
  <el-form
    @submit.prevent
    :model="modelValue"
    label-position="top"
    require-asterisk-position="right"
    label-width="auto"
    hide-required-asterisk
    ref="applicationParameterFormRef"
  >
    <template v-for="(f, index) in base_field_list" :key="f.field">
      <el-form-item
        v-if="modelValue[f.field]"
        :label="$t('workflow.nodes.startNode.question')"
        :prop="`${f.field}.value`"
        :rules="{
          message: `${f.label.value}为必填参数`,
          trigger: 'blur',
          required: f.required,
        }"
      >
        <template #label>
          <div class="flex-between">
            <div>
              {{ f.label.value }}
              <span class="color-danger" v-if="f.required">*</span>
            </div>
            <el-select
              :teleported="false"
              v-if="modelValue[f.field]"
              v-model="modelValue[f.field].source"
              size="small"
              style="width: 85px"
            >
              <el-option label="引用" value="reference" />
              <el-option :label="$t('common.custom')" value="custom" />
            </el-select>
          </div>
        </template>

        <el-cascader
          v-if="modelValue[f.field].source === 'reference'"
          v-model="modelValue[f.field].value"
          :options="options"
          :placeholder="$t('views.tool.form.param.selectPlaceholder')"
          :props="props"
        />
        <el-input
          v-else
          v-model="modelValue[f.field].value"
          :placeholder="$t('views.tool.form.param.inputPlaceholder')"
        />
      </el-form-item>
    </template>
    <template v-for="(f, index) in user_input_field_list" :key="f.field">
      <el-form-item
        v-if="modelValue['user_input_field_list'] && modelValue['user_input_field_list'][f.field]"
        :label="$t('workflow.nodes.startNode.question')"
        :prop="`user_input_field_list.${f.field}.value`"
        :rules="{
          message: `${f.label.value}为必填参数`,
          trigger: 'blur',
          required: f.required,
        }"
      >
        <template #label>
          <div class="flex-between">
            <div>
              {{ f.label.value }}
              <span class="color-danger" v-if="f.required">*</span>
            </div>
            <el-select
              :teleported="false"
              v-if="modelValue['user_input_field_list'][f.field]"
              v-model="modelValue['user_input_field_list'][f.field].source"
              size="small"
              style="width: 85px"
            >
              <el-option label="引用" value="reference" />
              <el-option :label="$t('common.custom')" value="custom" />
            </el-select>
          </div>
        </template>

        <el-cascader
          v-if="modelValue['user_input_field_list'][f.field].source === 'reference'"
          v-model="modelValue[f.field].value"
          :options="options"
          :placeholder="$t('views.tool.form.param.selectPlaceholder')"
          :props="props"
        />
        <el-input
          v-else
          v-model="modelValue['user_input_field_list'][f.field].value"
          :placeholder="$t('views.tool.form.param.inputPlaceholder')"
        />
      </el-form-item>
    </template>
    <template v-for="(f, index) in api_input_field_list" :key="f.field">
      <el-form-item
        v-if="modelValue['api_input_field_list'] && modelValue['api_input_field_list'][f.field]"
        :label="$t('workflow.nodes.startNode.question')"
        :prop="`api_input_field_list.${f.field}.value`"
        :rules="{
          message: `${f.label.value}为必填参数`,
          trigger: 'blur',
          required: f.required,
        }"
      >
        <template #label>
          <div class="flex-between">
            <div>
              {{ f.label.value }}
              <span class="color-danger" v-if="f.required">*</span>
            </div>
            <el-select
              :teleported="false"
              v-if="modelValue['api_input_field_list'][f.field]"
              v-model="modelValue['api_input_field_list'][f.field].source"
              size="small"
              style="width: 85px"
            >
              <el-option label="引用" value="reference" />
              <el-option :label="$t('common.custom')" value="custom" />
            </el-select>
          </div>
        </template>

        <el-cascader
          v-if="modelValue['api_input_field_list'][f.field].source === 'reference'"
          v-model="modelValue[f.field].value"
          :options="options"
          :placeholder="$t('views.tool.form.param.selectPlaceholder')"
          :props="props"
        />
        <el-input
          v-else
          v-model="modelValue['api_input_field_list'][f.field].value"
          :placeholder="$t('views.tool.form.param.inputPlaceholder')"
        />
      </el-form-item>
    </template>
  </el-form>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { type FormInstance } from 'element-plus'
const applicationParameterFormRef = ref<FormInstance>()
const props = defineProps<{ application?: any; modelValue: any; trigger: any }>()
const emit = defineEmits(['update:modelValue'])

const options = computed(() => {
  if (props.trigger.trigger_type === 'EVENT') {
    const body = props.trigger.trigger_setting.body
    if (body) {
      return [
        {
          label: 'body',
          value: 'body',
          children: body.map((item: any) => ({ label: item.field, value: item.field })),
        },
      ]
    }
    return []
  } else {
  }
  return []
})

const base_node = computed(() => {
  return (props.application?.work_flow?.nodes || []).find((n: any) => n.type === 'base-node')
})
const api_input_field_list = computed(() => {
  const result: Array<any> = []
  if (base_node.value && base_node.value.properties.api_input_field_list) {
    base_node.value.properties.api_input_field_list.forEach((item: any) => {
      result.push({
        field: item.variable,
        required: item.is_required,
        label: { value: item.variable },
      })
    })
  }
  return result
})
const user_input_field_list = computed(() => {
  const result: Array<any> = []
  if (base_node.value && base_node.value.properties.user_input_field_list) {
    base_node.value.properties.user_input_field_list.forEach((item: any) => {
      result.push({
        field: item.field,
        required: item.required,
        label:
          typeof item.label == 'string'
            ? { value: item.label }
            : { ...item.label, value: item.label.label },
      })
    })
  }
  return result
})
const base_field_list = computed<Array<any>>(() => {
  const result: Array<any> = [
    { field: 'question', required: true, default_value: '', label: { value: 'Question' } },
  ]
  if (base_node.value) {
    if (base_node.value.properties.node_data.file_upload_enable) {
      if (base_node.value.properties.node_data.file_upload_setting.document) {
        result.push({
          field: 'document',
          required: true,
          default_value: '[]',
          label: { value: '文档' },
        })
      }
      if (base_node.value.properties.node_data.file_upload_setting.image) {
        result.push({
          field: 'image',
          required: true,
          default_value: '[]',
          label: { value: '图片' },
        })
      }
      if (base_node.value.properties.node_data.file_upload_setting.audio) {
        result.push({
          field: 'audio',
          required: true,
          default_value: '[]',
          label: { value: '音频' },
        })
      }
      if (base_node.value.properties.node_data.file_upload_setting.video) {
        result.push({
          field: 'video',
          required: true,
          default_value: '[]',
          label: { value: '视频' },
        })
      }

      if (base_node.value.properties.node_data.file_upload_setting.other) {
        result.push({
          field: 'other',
          required: true,
          default_value: '[]',
          label: { value: '其他' },
        })
      }
    }
  }
  return result
})
const init_parameters = () => {
  const parameter: any = {}
  base_field_list.value.forEach((f) => {
    parameter[f.field] = { source: 'custom', value: f.default_value }
  })
  api_input_field_list.value.forEach((f) => {
    if (!parameter.api_input_field_list) {
      parameter['api_input_field_list'] = {}
    }
    parameter['api_input_field_list'][f.field] = {
      source: 'custom',
      value: f.default_value ? f.default_value : '',
    }
  })
  user_input_field_list.value.forEach((f) => {
    if (!parameter['user_input_field_list']) {
      parameter['user_input_field_list'] = {}
    }
    parameter['user_input_field_list'][f.field] = {
      source: 'custom',
      value: f.default_value ? f.default_value : '',
    }
  })
  emit('update:modelValue', { ...parameter, ...props.modelValue })
}

init_parameters()
const validate = () => {
  return applicationParameterFormRef.value?.validate()
}
defineExpose({ validate })
</script>
<style lang=""></style>
