<template>
  <el-form-item v-if="getModel">
    <template #label>
      <div class="flex-between">
        {{ $t('dynamicsForm.AssignmentMethod.label', '赋值方式') }}
      </div>
    </template>

    <el-row style="width: 100%" :gutter="10">
      <el-radio-group @change="formValue.option_list = []" v-model="formValue.assignment_method">
        <el-radio :value="item.value" size="large" v-for="item in assignment_method_option_list"
          >{{ item.label }}
          <el-popover
            width="300px"
            v-if="item.value == 'ref_variables'"
            class="box-item"
            placement="top-start"
          >
            {{ $t('dynamicsForm.AssignmentMethod.ref_variables.popover') }}:<br />
            [<br />
            {<br />
            "label": "xx",<br />
            "value": "xx",<br />
            "default": false<br />
            }<br />
            ]<br />
            label: {{ $t('dynamicsForm.AssignmentMethod.ref_variables.popover_label') }}
            {{ $t('common.required') }}<br />
            value: {{ $t('dynamicsForm.AssignmentMethod.ref_variables.popover_value') }}
            {{ $t('common.required') }}<br />
            default: {{ $t('dynamicsForm.AssignmentMethod.ref_variables.popover_default') }}
            <template #reference>
              <el-icon><InfoFilled /></el-icon>
            </template> </el-popover
        ></el-radio>
      </el-radio-group>
    </el-row>
  </el-form-item>
  <el-form-item
    v-if="formValue.assignment_method == 'ref_variables'"
    :required="true"
    prop="option_list"
    :rules="[default_ref_variables_value_rule]"
  >
    <NodeCascader
      ref="nodeCascaderRef"
      :nodeModel="model"
      class="w-full"
      :placeholder="$t('views.applicationWorkflow.variable.placeholder')"
      v-model="formValue.option_list"
    />
  </el-form-item>
  <el-form-item v-if="formValue.assignment_method == 'custom'">
    <template #label>
      <div class="flex-between">
        {{ $t('dynamicsForm.Select.label') }}
        <el-button link type="primary" @click.stop="addOption()">
          <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
          {{ $t('common.add') }}
        </el-button>
      </div>
    </template>

    <el-row style="width: 100%" :gutter="10">
      <el-col :span="10">
        <div class="grid-content ep-bg-purple" />
        {{ $t('dynamicsForm.tag.label') }}
      </el-col>
      <el-col :span="12">
        <div class="grid-content ep-bg-purple" />
        {{ $t('dynamicsForm.Select.label') }}
      </el-col>
    </el-row>
    <el-row
      style="width: 100%"
      v-for="(option, $index) in formValue.option_list"
      :key="$index"
      :gutter="10"
      class="mb-8"
    >
      <el-col :span="10">
        <div class="grid-content ep-bg-purple" />
        <el-input
          v-model="formValue.option_list[$index].label"
          :placeholder="$t('dynamicsForm.tag.placeholder')"
        />
      </el-col>
      <el-col :span="12">
        <div class="grid-content ep-bg-purple" />
        <el-input
          v-model="formValue.option_list[$index].value"
          :placeholder="$t('dynamicsForm.Select.label')"
        />
      </el-col>
      <el-col :span="1">
        <div class="grid-content ep-bg-purple" />
        <el-button link class="ml-8" @click.stop="delOption($index)">
          <AppIcon iconName="app-delete"></AppIcon>
        </el-button>
      </el-col>
    </el-row>
  </el-form-item>
  <el-form-item
    v-if="formValue.assignment_method == 'custom'"
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    :label="$t('dynamicsForm.default.label')"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: `${$t('dynamicsForm.default.label')}${$t('dynamicsForm.default.requiredMessage')}`,
            },
          ]
        : []
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox
        v-model="formValue.show_default_value"
        :label="$t('dynamicsForm.default.show')"
      />
    </div>

    <el-select v-model="formValue.default_value" :teleported="false" popper-class="default-select">
      <el-option
        v-for="(option, index) in formValue.option_list"
        :key="index"
        :label="option.label"
        :value="option.value"
      />
    </el-select>
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onMounted, inject, watch } from 'vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import { t } from '@/locales'
const getModel = inject('getModel') as any

const assignment_method_option_list = computed(() => {
  const option_list = [
    {
      label: t('common.custom'),
      value: 'custom',
    },
  ]
  if (getModel) {
    option_list.push({
      label: t('views.applicationWorkflow.variable.Referencing'),
      value: 'ref_variables',
    })
  }
  return option_list
})

const model = computed(() => {
  if (getModel) {
    return getModel()
  } else {
    return null
  }
})
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const default_ref_variables_value_rule = {
  required: true,
  validator: (rule: any, value: any, callback: any) => {
    console.log(value.length)
    if (!(Array.isArray(value) && value.length > 1)) {
      callback(
        t('views.applicationWorkflow.variable.Referencing') + t('common.required'),
      )
    }

    return true
  },
  trigger: 'blur',
}
const addOption = () => {
  formValue.value.option_list.push({ value: '', label: '' })
}

const delOption = (index: number) => {
  const option = formValue.value.option_list[index]
  if (option.value && formValue.value.default_value == option.value) {
    formValue.value.default_value = ''
  }
  formValue.value.option_list.splice(index, 1)
}

const getData = () => {
  return {
    input_type: 'SingleSelect',
    attrs: {},
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    text_field: 'label',
    value_field: 'value',
    option_list: formValue.value.option_list,
    assignment_method: formValue.value.assignment_method || 'custom',
  }
}
const rander = (form_data: any) => {
  formValue.value.option_list = form_data.option_list || []
  formValue.value.default_value = form_data.default_value
  formValue.value.show_default_value = form_data.show_default_value
  formValue.value.assignment_method = form_data.assignment_method || 'custom'
}

defineExpose({ getData, rander })
onMounted(() => {
  formValue.value.option_list = []
  formValue.value.default_value = ''
  formValue.value.assignment_method = 'custom'
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
  addOption()
})
</script>
<style lang="scss" scoped>
.defaultValueItem {
  position: relative;
  .defaultValueCheckbox {
    position: absolute;
    right: 0;
    top: -35px;
  }
}
:deep(.el-form-item__label) {
  display: block;
}

:deep(.el-select-dropdown) {
  max-width: 400px;
}
</style>
