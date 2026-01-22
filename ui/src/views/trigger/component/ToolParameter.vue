<template>
  <el-form
    @submit.prevent
    :model="modelValue"
    label-position="top"
    require-asterisk-position="right"
    label-width="auto"
    hide-required-asterisk
    ref="toolParameterFormRef"
  >
    <template v-for="(f, index) in input_field_list" :key="f.field">
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
  </el-form>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { type FormInstance } from 'element-plus'
const toolParameterFormRef = ref<FormInstance>()
const props = defineProps<{ tool?: any; modelValue: any; trigger: any }>()
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

const input_field_list = computed(() => {
  const result: Array<any> = []
  if (props.tool && props.tool.input_field_list) {
    props.tool.input_field_list.forEach((item: any) => {
      result.push({
        field: item.name,
        required: item.is_required,
        label: { value: item.name },
      })
    })
  }
  return result
})

const init_parameters = () => {
  const parameter: any = {}
  input_field_list.value.forEach((f) => {
    parameter[f.field] = { source: 'custom', value: f.default_value }
  })
  emit('update:modelValue', { ...parameter, ...props.modelValue })
}

init_parameters()
const validate = () => {
  return toolParameterFormRef.value?.validate()
}
defineExpose({ validate })
</script>
<style lang="scss"></style>
