<template>
  <div class="w-full">
    <el-select
      v-model="modelValue"
      popper-class="select-model"
      :clearable="true"
      filterable
      v-bind="$attrs"
    >
      <el-option-group
        v-for="(value, label) in options"
        :key="value"
        :label="relatedObject(providerOptions, label, 'provider')?.name"
      >
        <el-option
          v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
          :key="item.id"
          :label="item.name"
          :value="item.id"
          class="flex-between"
        >
          <el-space :size="8">
            <span
              :innerHTML="relatedObject(providerOptions, label, 'provider')?.icon"
              class="select-model-icon"
              style="margin-top: -7px"
            ></span>
            <span>{{ item.name }}</span>
            <el-tag v-if="item.type === 'share'" type="info" class="info-tag">
              {{ t('views.shared.title') }}
            </el-tag>
          </el-space>

          <el-icon class="check-icon" v-if="item.id === modelValue">
            <Check />
          </el-icon>
        </el-option>
        <!-- 不可用 -->
        <el-option
          v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
          :key="item.id"
          :label="item.name"
          :value="item.id"
          class="flex-between"
          disabled
        >
          <el-space :size="8">
            <span
              :innerHTML="relatedObject(providerOptions, label, 'provider')?.icon"
              class="select-model-icon"
              style="margin-top: -7px"
            ></span>
            <span>{{ item.name }}</span>
            <span class="color-danger">{{ $t('common.unavailable') }}</span>
          </el-space>
          <el-icon class="check-icon" v-if="item.id === modelValue">
            <Check />
          </el-icon>
        </el-option>
      </el-option-group>

      <template #label="{ label, value }">
        <el-space :size="8">
          <span
            class="select-model-icon"
            :innerHTML="relatedObject(providerOptions, getModelProvider(value), 'provider')?.icon"
          >
          </span>
          <span>
            <span>{{
              relatedObject(providerOptions, getModelProvider(value), 'provider')?.name
            }}</span>
            <span>/</span>
            <span>{{ label }}</span>
          </span>
        </el-space>
      </template>

      <template #footer v-if="showFooter">
        <slot name="footer">
          <div class="w-full text-left cursor" @click="openCreateModel(undefined, props.modelType)">
            <el-button type="primary" link v-if="permissionPrecise.create()">
              <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
              {{ $t('views.application.operation.addModel') }}
            </el-button>
          </div>
        </slot>
      </template>
    </el-select>
    <!-- 添加模板 -->
    <CreateModelDialog
      v-if="showFooter"
      ref="createModelRef"
      @submit="submitModel"
      @change="openCreateModel($event)"
    ></CreateModelDialog>
    <SelectProviderDialog
      v-if="showFooter"
      ref="selectProviderRef"
      @change="(provider, modelType) => openCreateModel(provider, modelType)"
    />
  </div>
</template>
<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import type { Provider } from '@/api/type/model'
import { relatedObject } from '@/utils/array'
import CreateModelDialog from '@/views/model/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/model/component/SelectProviderDialog.vue'
import { flatMap } from 'lodash'
import { t } from '@/locales'
import useStore from '@/stores'
import permissionMap from '@/permission'

defineOptions({ name: 'ModelSelect' })
const props = defineProps<{
  modelValue: any
  options: any
  showFooter?: false
  modelType?: ''
}>()

const permissionPrecise = computed(() => {
  return permissionMap['model']['workspace']
})

const emit = defineEmits(['update:modelValue', 'change', 'submitModel'])
const modelValue = computed({
  set: (item) => {
    emit('change', item)
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})
const { model } = useStore()

const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()
const providerOptions = ref<Array<Provider>>([])
const loading = ref(false)

function getProvider() {
  loading.value = true
  model
    .asyncGetProvider()
    .then((res: any) => {
      providerOptions.value = res?.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

const openCreateModel = (provider?: Provider, model_type?: string) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider, model_type)
  } else {
    selectProviderRef.value?.open(model_type)
  }
}
const getModelProvider = computed(() => {
  return (id: string) => {
    const item = flatMap(props.options)?.find((item: any) => item.id === id)
    return (item as any)?.provider || ''
  }
})

function submitModel() {
  emit('submitModel')
}

onMounted(() => {
  getProvider()
})
</script>
<style lang="scss" scoped>
// AI模型选择：添加模型hover样式
.select-model {
  .el-select-dropdown__footer {
    &:hover {
      background-color: var(--el-fill-color-light);
    }
  }

  .check-icon {
    position: absolute;
    right: 10px;
  }
}
</style>
