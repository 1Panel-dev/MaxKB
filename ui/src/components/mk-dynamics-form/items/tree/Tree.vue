<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, ref, useAttrs, nextTick, inject } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { get, post, put, del } from '@/api/admin/core/request'
import { cloneDeep } from 'lodash'
import { formItemContextKey } from 'element-plus'
import type { LoadFunction } from 'element-plus'
const getExtra = inject('get_extra') as DynamicFormValue
const elFormItem = inject(formItemContextKey, void 0)
const request = { get, post, put, del }

defineOptions({ name: 'DynamicFormTree' })

const allCheck = ref<boolean>(false)

const handleAllCheckChange = (checked: boolean) => {
  if (checked) {
    const nodes = Object.values(treeRef.value?.store.nodesMap || {}) as DynamicFormValue[]
    nodes.forEach((node) => {
      if (!node.disabled) {
        treeRef.value?.setChecked(node.data, true, false)
      }
    })
  } else {
    treeRef.value?.setCheckedKeys([])
  }
}
const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'label'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})
const childrenField = computed(() => {
  return props.formField.childrenField ? props.formField.childrenField : 'children'
})
const options = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
const propsData = computed(() => {
  return { label: textField, children: childrenField, isLeaf: (data: DynamicFormValue) => data.leaf, disabled: (data: DynamicFormValue) => data.disabled }
})

const attrs = useAttrs() as DynamicFormValue
const treeRef = ref<DynamicFormValue>(null)
const requestCall = new Function('request', 'extra', 'return  request.post(extra.url,extra.body,{},extra.loading).then(extra.then);')
function renderTemplate(template: string, data: DynamicFormValue) {
  return template.replace(/\$\{(\w+)\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match
  })
}

const loadNode: LoadFunction = (node, resolve) => {
  requestCall(request, {
    url: renderTemplate('/workspace/${current_workspace_id}/knowledge/${current_knowledge_id}/datasource/tool/${current_tool_id}/' + attrs.fetch_list_function, {
      ...props.otherParams,
      ...(getExtra ? getExtra() : {}),
    }),
    body: { current_node: node.level === 0 ? undefined : node.data },
    then: (res: DynamicFormValue) => {
      resolve(res.data)
      res.data.forEach((childNode: DynamicFormValue) => {
        if (childNode.is_exist) {
          treeRef.value?.setChecked(childNode.token, true, false)
        }
      })
    },
    loading: loading,
  })
}
const props = withDefaults(defineProps<{ modelValue?: DynamicFormValue; formField: FormField; otherParams: DynamicFormValue }>(), { modelValue: () => [] })

const emit = defineEmits(['update:modelValue', 'change'])

const modelValueProxy = computed({
  get: () => {
    if (!props.modelValue) {
      emit('update:modelValue', [])
    }
    return props.modelValue
  },
  set: (v: DynamicFormValue[]) => {
    emit('update:modelValue', v)
  },
})
const change = () => {
  modelValueProxy.value = cloneDeep(treeRef.value?.getCheckedNodes() || [])
  nextTick(() => {
    if (elFormItem?.validate) {
      elFormItem.validate('change')
    }
  })
}

const loading = ref<boolean>(false)
</script>

<template>
  <div v-loading="loading" class="w-full">
    <div class="card-never border-r-6 mb-16">
      <el-checkbox v-model="allCheck" label="全选" size="large" class="ml-24" @change="handleAllCheckChange" />
    </div>
    <div style="height: calc(100vh - 450px)">
      <el-scrollbar>
        <el-tree
          :data="options"
          @check-change="change"
          v-loading="loading"
          style="width: 100%"
          :props="propsData"
          :load="loadNode"
          :lazy="attrs.lazy"
          show-checkbox
          :node-key="valueField"
          ref="treeRef"
        >
          <template #default="{ node, data }">
            <div class="flex align-center lighter">
              <img :src="data.icon" alt="" height="20" v-if="data.icon" />
              <img src="@/assets/empty/no-data.svg" alt="" height="20" v-else-if="data.type === 'folder'" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.type === 'docx' || data.name.endsWith('.docx')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.type === 'sheet' || data.name.endsWith('.xlsx')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('xls')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('csv')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('.pdf')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('.html')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('.txt')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('.zip')" />
              <img src="@/assets/empty/no-data.svg" alt="" height="22" v-else-if="data.name.endsWith('.md')" />

              <span class="ml-4">{{ node.label }}</span>
            </div>
          </template>
        </el-tree></el-scrollbar
      >
    </div>
  </div>
</template>
