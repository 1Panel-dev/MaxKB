<template>
  <div
    v-if="
      (inputFieldList.length > 0 || (type === 'debug-ai-chat' && apiInputFieldList.length > 0)) &&
      type !== 'log'
    "
    class="user-form-container mb-16 w-full"
  >
    <el-card shadow="always" class="border-r-8" style="--el-card-padding: 16px 8px">
      <div class="flex align-center cursor w-full" style="padding: 0 8px">
        <span class="break-all ellipsis-1 mr-16" :title="inputFieldConfig.title">
          {{ inputFieldConfig.title }}
        </span>
      </div>

      <el-scrollbar :max-height="first ? '' : 450">
        <div class="mt-16" style="padding: 0 8px; height: calc(100% - 100px)">
          <DynamicsForm
            :key="dynamicsFormRefresh"
            v-model="form_data_context"
            :model="form_data_context"
            label-position="top"
            require-asterisk-position="right"
            :render_data="inputFieldList"
            ref="dynamicsFormRef"
          />
          <DynamicsForm
            v-if="type === 'debug-ai-chat'"
            v-model="api_form_data_context"
            :model="api_form_data_context"
            label-position="top"
            require-asterisk-position="right"
            :render_data="apiInputFieldList"
            ref="dynamicsFormRef2"
          />
        </div>
      </el-scrollbar>

      <div class="text-left ml-8">
        <el-button type="primary" class="w-full" v-if="first" @click="confirmHandle">
          <AppIcon iconName="app-chat" class="mr-4"></AppIcon>
          {{ $t('chat.operation.startChat') }}</el-button
        >
        <el-button type="primary" v-if="!first" @click="confirmHandle">{{
          $t('common.confirm')
        }}</el-button>
        <el-button v-if="!first" @click="cancelHandle">{{ $t('common.cancel') }}</el-button>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import DynamicsForm from '@/components/dynamics-form/index.vue'
import type { FormField } from '@/components/dynamics-form/type'
import { useRoute } from 'vue-router'
import { MsgWarning } from '@/utils/message'
import { t } from '@/locales'
const route = useRoute()
const {
  params: { accessToken },
} = route
const props = defineProps<{
  application: any
  type: 'log' | 'ai-chat' | 'debug-ai-chat'
  api_form_data: any
  form_data: any
  first?: boolean
}>()
// 用于刷新动态表单
const dynamicsFormRefresh = ref(0)
const inputFieldList = ref<FormField[]>([])
const apiInputFieldList = ref<FormField[]>([])
const inputFieldConfig = ref({ title: t('chat.userInput') })
const firstMounted = ref(false)

const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
const dynamicsFormRef2 = ref<InstanceType<typeof DynamicsForm>>()

const emit = defineEmits(['update:api_form_data', 'update:form_data', 'confirm', 'cancel'])

const api_form_data_context = computed({
  get: () => {
    return props.api_form_data
  },
  set: (data) => {
    emit('update:api_form_data', data)
  },
})

const form_data_context = computed({
  get: () => {
    return props.form_data
  },
  set: (data) => {
    emit('update:form_data', data)
  },
})

watch(
  () => props.application,
  (data) => {
    handleInputFieldList()
  },
)

function handleInputFieldList() {
  dynamicsFormRefresh.value++
  const default_value: any = {}
  props.application.work_flow?.nodes
    ?.filter((v: any) => v.id === 'base-node')
    .map((v: any) => {
      inputFieldList.value = v.properties.user_input_field_list
        ? v.properties.user_input_field_list.map((v: any) => {
            switch (v.type) {
              case 'input':
                return {
                  field: v.variable,
                  input_type: 'TextInput',
                  label: v.name,
                  default_value: default_value[v.variable],
                  required: v.is_required,
                }
              case 'select':
                return {
                  field: v.variable,
                  input_type: 'SingleSelect',
                  label: v.name,
                  default_value: default_value[v.variable],
                  required: v.is_required,
                  option_list: v.optionList.map((o: any) => {
                    return { key: o, value: o }
                  }),
                }
              case 'date':
                return {
                  field: v.variable,
                  input_type: 'DatePicker',
                  label: v.name,
                  default_value: default_value[v.variable],
                  required: v.is_required,
                  attrs: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    'value-format': 'YYYY-MM-DD HH:mm:ss',
                    type: 'datetime',
                  },
                }
              default:
                return v
            }
          })
        : v.properties.input_field_list
          ? v.properties.input_field_list
              .filter((v: any) => v.assignment_method === 'user_input')
              .map((v: any) => {
                switch (v.type) {
                  case 'input':
                    return {
                      field: v.variable,
                      input_type: 'TextInput',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                    }
                  case 'select':
                    return {
                      field: v.variable,
                      input_type: 'SingleSelect',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                      option_list: v.optionList.map((o: any) => {
                        return { key: o, value: o }
                      }),
                    }
                  case 'date':
                    return {
                      field: v.variable,
                      input_type: 'DatePicker',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                      attrs: {
                        format: 'YYYY-MM-DD HH:mm:ss',
                        'value-format': 'YYYY-MM-DD HH:mm:ss',
                        type: 'datetime',
                      },
                    }
                  default:
                    break
                }
              })
          : []

      apiInputFieldList.value = v.properties.api_input_field_list
        ? v.properties.api_input_field_list.map((v: any) => {
            switch (v.type) {
              case 'input':
                return {
                  field: v.variable,
                  input_type: 'TextInput',
                  label: v.variable,
                  default_value: v.default_value || default_value[v.variable],
                  required: v.is_required,
                }
              case 'select':
                return {
                  field: v.variable,
                  input_type: 'SingleSelect',
                  label: v.variable,
                  default_value: v.default_value || default_value[v.variable],
                  required: v.is_required,
                  option_list: v.optionList.map((o: any) => {
                    return { key: o, value: o }
                  }),
                }
              case 'date':
                return {
                  field: v.variable,
                  input_type: 'DatePicker',
                  label: v.variable,
                  default_value: v.default_value || default_value[v.variable],
                  required: v.is_required,
                  attrs: {
                    format: 'YYYY-MM-DD HH:mm:ss',
                    'value-format': 'YYYY-MM-DD HH:mm:ss',
                    type: 'datetime',
                  },
                }
              default:
                break
            }
          })
        : v.properties.input_field_list
          ? v.properties.input_field_list
              .filter((v: any) => v.assignment_method === 'api_input')
              .map((v: any) => {
                switch (v.type) {
                  case 'input':
                    return {
                      field: v.variable,
                      input_type: 'TextInput',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                    }
                  case 'select':
                    return {
                      field: v.variable,
                      input_type: 'SingleSelect',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                      option_list: v.optionList.map((o: any) => {
                        return { key: o, value: o }
                      }),
                    }
                  case 'date':
                    return {
                      field: v.variable,
                      input_type: 'DatePicker',
                      label: v.name,
                      default_value: default_value[v.variable],
                      required: v.is_required,
                      attrs: {
                        format: 'YYYY-MM-DD HH:mm:ss',
                        'value-format': 'YYYY-MM-DD HH:mm:ss',
                        type: 'datetime',
                      },
                    }
                  default:
                    break
                }
              })
          : []

      //
      inputFieldConfig.value = v.properties.user_input_config?.title
        ? v.properties.user_input_config
        : { title: t('chat.userInput') }
    })
}
const getRouteQueryValue = (field: string) => {
  let _value = route.query[field]
  if (_value != null) {
    if (_value instanceof Array) {
      _value = _value
        .map((item) => {
          if (item != null) {
            return decodeQuery(item)
          }
          return null
        })
        .filter((item) => item != null)
    } else {
      _value = decodeQuery(_value)
    }
    return _value
  }
  return null
}
const validate = () => {
  const promise_list = []
  if (dynamicsFormRef.value) {
    promise_list.push(dynamicsFormRef.value?.validate())
  }
  if (dynamicsFormRef2.value) {
    promise_list.push(dynamicsFormRef2.value?.validate())
  }
  promise_list.push(validate_query())
  return Promise.all(promise_list)
}
const validate_query = () => {
  // 浏览器query参数找到接口传参
  const msg = []
  for (const f of apiInputFieldList.value) {
    if (f.required && !api_form_data_context.value[f.field]) {
      msg.push(f.field)
    }
  }
  if (msg.length > 0) {
    MsgWarning(
      `${t('chat.tip.inputParamMessage1')} ${msg.join('、')}${t('chat.tip.inputParamMessage2')}`,
    )
    return Promise.reject(false)
  }
  return Promise.resolve(false)
}

const initRouteQueryValue = () => {
  for (const f of apiInputFieldList.value) {
    if (!api_form_data_context.value[f.field]) {
      const _value = getRouteQueryValue(f.field)
      if (_value != null) {
        api_form_data_context.value[f.field] = _value
      }
    }
  }
  if (!api_form_data_context.value['asker']) {
    const asker = getRouteQueryValue('asker')
    if (asker) {
      api_form_data_context.value['asker'] = getRouteQueryValue('asker')
    }
  }
}

const decodeQuery = (query: string) => {
  try {
    return decodeURIComponent(query)
  } catch (e) {
    return query
  }
}
const confirmHandle = () => {
  validate().then((ok) => {
    localStorage.setItem(`${accessToken}userForm`, JSON.stringify(form_data_context.value))
    emit('confirm')
  })
}
const cancelHandle = () => {
  emit('cancel')
}
const render = (data: any) => {
  if (dynamicsFormRef.value) {
    dynamicsFormRef.value?.render(inputFieldList.value, data)
  }
}

const renderDebugAiChat = (data: any) => {
  if (dynamicsFormRef2.value) {
    dynamicsFormRef2.value?.render(apiInputFieldList.value, data)
  }
}
defineExpose({ validate, render, renderDebugAiChat })
onMounted(() => {
  firstMounted.value = true
  handleInputFieldList()
  initRouteQueryValue()
})
</script>
<style lang="scss" scoped>
.user-form-container {
  padding: 0 24px;
}
@media only screen and (max-width: 768px) {
  .user-form-container {
    max-width: 100%;
  }
}
</style>
