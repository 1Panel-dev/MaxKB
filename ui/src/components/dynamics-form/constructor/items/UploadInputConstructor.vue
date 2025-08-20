<template>
  <el-form-item :label="$t('dynamicsForm.UploadInput.limit.label')" required prop="limit">
    <el-input-number
      style="width: 100%"
      v-model="formValue.limit"
      :rules="[
        {
          required: true,
          message: $t('dynamicsForm.UploadInput.limit.required'),
          trigger: 'change',
        },
      ]"
      :min="0"
      controls-position="right"
    />
  </el-form-item>
  <el-form-item
    :label="$t('dynamicsForm.UploadInput.max_file_size.label')"
    required
    prop="max_file_size"
    :rules="[
      {
        required: true,
        message: $t('dynamicsForm.UploadInput.max_file_size.required'),
        trigger: 'change',
      },
    ]"
  >
    <el-input-number
      style="width: 100%"
      v-model="formValue.max_file_size"
      :min="0"
      controls-position="right"
    />
  </el-form-item>
  <el-form-item
    :label="$t('dynamicsForm.UploadInput.accept.label')"
    required
    prop="accept"
    :rules="[
      {
        required: true,
        message: $t('dynamicsForm.UploadInput.accept.required'),
        trigger: 'change',
      },
    ]"
  >
    <div class="gap-2" style="display: flex">
      <el-tag
        v-for="tag in formValue.accept"
        :key="tag"
        closable
        :disable-transitions="false"
        @close="handleClose(tag)"
      >
        {{ tag }}
      </el-tag>
      <el-input
        v-if="inputVisible"
        ref="InputRef"
        v-model="inputValue"
        class="w-20"
        size="small"
        @keyup.enter="handleInputConfirm"
        @blur="handleInputConfirm"
      />
      <el-button v-else class="button-new-tag" size="small" @click="showInput">
        + {{ $t('common.fileUpload.addExtensions') }}
      </el-button>
    </div>
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue'
import { ElMessage, type InputInstance } from 'element-plus'
import { t } from '@/locales'
const props = defineProps<{
  modelValue: any
}>()

const inputValue = ref('')

const inputVisible = ref(false)
const InputRef = ref<InputInstance>()
const handleClose = (tag: string) => {
  formValue.value.accept.splice(formValue.value.accept.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}

const handleInputConfirm = () => {
  if (formValue.value.accept.find((item: string) => item === inputValue.value)) {
    ElMessage.warning(t('common.fileUpload.existingExtensionsTip'))
    return
  }
  if (inputValue.value) {
    formValue.value.accept.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const rander = (form_data: any) => {
  formValue.value.default_value = []
  formValue.value.limit = form_data.attrs.limit || 3
  formValue.value.max_file_size = form_data.max_file_size || 10
  formValue.value.accept = form_data.attrs.accept
    ? form_data.attrs.accept.split(',').map((item: string) => item.substring(1))
    : ['jpg']
}
const getData = () => {
  return {
    input_type: 'UploadInput',
    attrs: {
      accept: formValue.value.accept.map((item: any) => '.' + item).join(','),
      limit: formValue.value.limit,
    },
    max_file_size: formValue.value.max_file_size,
    default_value: [],
    show_default_value: formValue.value.show_default_value,
  }
}
defineExpose({ getData, rander })

onMounted(() => {
  formValue.value.default_value = []
  formValue.value.limit = 3
  formValue.value.max_file_size = 10
  formValue.value.accept = ['jpg']
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>
<style lang="scss" scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>
