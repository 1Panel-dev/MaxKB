<template>
  <div v-loading="loading" class="w-full">
    <div class="card-never border-r-6 mb-16">
      <el-checkbox
        v-model="allCheck"
        :label="$t('views.document.feishu.allCheck')"
        size="large"
        class="ml-24"
        @change="handleAllCheckChange"
      />
    </div>
    <div style="height: calc(100vh - 450px)">
      <el-scrollbar>
        <el-tree
          :data="option_list"
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
              <img
                src="@/assets/fileType/file-icon.svg"
                alt=""
                height="20"
                v-else-if="data.type === 'folder'"
              />
              <img
                src="@/assets/fileType/docx-icon.svg"
                alt=""
                height="22"
                v-else-if="data.type === 'docx' || data.name.endsWith('.docx')"
              />
              <img
                src="@/assets/fileType/xlsx-icon.svg"
                alt=""
                height="22"
                v-else-if="data.type === 'sheet' || data.name.endsWith('.xlsx')"
              />
              <img
                src="@/assets/fileType/xls-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('xls')"
              />
              <img
                src="@/assets/fileType/csv-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('csv')"
              />
              <img
                src="@/assets/fileType/pdf-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('.pdf')"
              />
              <img
                src="@/assets/fileType/html-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('.html')"
              />
              <img
                src="@/assets/fileType/txt-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('.txt')"
              />
              <img
                src="@/assets/fileType/zip-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('.zip')"
              />
              <img
                src="@/assets/fileType/md-icon.svg"
                alt=""
                height="22"
                v-else-if="data.name.endsWith('.md')"
              />

              <span class="ml-4">{{ node.label }}</span>
            </div>
          </template>
        </el-tree></el-scrollbar
      >
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, useAttrs, nextTick, inject } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import type Node from 'element-plus/es/components/tree/src/model/node'
import { get, post, put, del } from '@/request/index'
import { cloneDeep } from 'lodash'
import { formItemContextKey } from 'element-plus'
const elFormItem = inject(formItemContextKey, void 0)
const request = {
  get,
  post,
  put,
  del,
}

const allCheck = ref<boolean>(false)

const handleAllCheckChange = (checked: boolean) => {
  if (checked) {
    const nodes = Object.values(treeRef.value?.store.nodesMap || {}) as any[]
    nodes.forEach((node) => {
      if (!node.disabled) {
        treeRef.value?.setChecked(node.data, true, false)
      }
    })
  } else {
    treeRef.value?.setCheckedKeys([])
  }
}
interface Tree {
  label: string
  leaf?: boolean
  type: string
  value: string
  disabled: boolean
  icon?: string
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
const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
const propsData = computed(() => {
  return {
    label: textField,
    children: childrenField,
    isLeaf: (data: any) => data.leaf,
    disabled: (data: any) => data.disabled,
  }
})

const attrs = useAttrs() as any
const treeRef = ref<any>(null)
const request_call = new Function(
  'request',
  'extra',
  'return  request.post(extra.url,extra.body,{},extra.loading).then(extra.then);',
)
function renderTemplate(template: string, data: any) {
  return template.replace(/\$\{(\w+)\}/g, (match, key) => {
    return data[key] !== undefined ? data[key] : match
  })
}

const loadNode = (node: Node, resolve: (nodeData: Tree[]) => void) => {
  request_call(request, {
    url: renderTemplate(attrs.url, props.otherParams),
    body: { current_node: node.level == 0 ? undefined : node.data },
    then: (res: any) => {
      resolve(res.data)
      res.data.forEach((childNode: any) => {
        if (childNode.is_exist) {
          treeRef.value?.setChecked(childNode.token, true, false)
        }
      })
    },
    loading: loading,
  })
}
const props = withDefaults(
  defineProps<{ modelValue?: any; formField: FormField; otherParams: any }>(),
  {
    modelValue: () => [],
  },
)

const emit = defineEmits(['update:modelValue', 'change'])

const model_value = computed({
  get: () => {
    if (!props.modelValue) {
      emit('update:modelValue', [])
    }
    return props.modelValue
  },
  set: (v: Array<any>) => {
    emit('update:modelValue', v)
  },
})
const change = () => {
  model_value.value = cloneDeep(treeRef.value?.getCheckedNodes() || [])
  nextTick(() => {
    if (elFormItem?.validate) {
      elFormItem.validate('change')
    }
  })
}

const loading = ref<boolean>(false)
</script>
<style lang="scss" scoped></style>
