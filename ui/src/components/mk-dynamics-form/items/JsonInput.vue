<script setup lang="ts">
import type { DynamicFormValue } from '../type'
import { json, jsonParseLinter } from '@codemirror/lang-json'
import { oneDark } from '@codemirror/theme-one-dark'
import { Codemirror } from 'vue-codemirror'
import { linter } from '@codemirror/lint'
import { computed, ref } from 'vue'
const props = withDefaults(defineProps<{ modelValue?: DynamicFormValue }>(), {
  modelValue: () => ({}),
})
const emit = defineEmits<{
  (event: 'update:modelValue', value: DynamicFormValue): void
}>()

const cachedModelValue = ref<string>()

const modelValueProxy = computed({
  get: () => {
    if (cachedModelValue.value) {
      return cachedModelValue.value
    }
    return JSON.stringify(props.modelValue, null, 4) ?? '{}'
  },
  set: (v: string) => {
    if (!v) {
      emit('update:modelValue', JSON.parse('{}'))
    } else {
      try {
        cachedModelValue.value = v
        const result = JSON.parse(v)
        emit('update:modelValue', result)
      } catch {}
    }
  },
})

const extensions = [json(), linter(jsonParseLinter()), oneDark]

const codemirrorStyle = {
  height: '210px!important',
  width: '100%',
}

// 弹出框相关代码
const dialogVisible = ref<boolean>(false)

const cloneContent = ref<string>('')

const openCodemirrorDialog = () => {
  cloneContent.value = modelValueProxy.value
  dialogVisible.value = true
}

const format = () => {
  try {
    const jsonValue = JSON.parse(modelValueProxy.value)
    modelValueProxy.value = JSON.stringify(jsonValue, null, 4)
  } catch {}
}

function submitDialog() {
  modelValueProxy.value = cloneContent.value
  dialogVisible.value = false
}
/**
 * 校验格式
 * @param rule
 * @param value
 * @param callback
 */
const validateRules = (
  _rule: unknown,
  _value: DynamicFormValue,
  callback: (error?: Error) => void,
) => {
  if (modelValueProxy.value) {
    try {
      JSON.parse(modelValueProxy.value)
    } catch {
      callback(new Error('JSON 格式不正确'))
      return false
    }
  }
  return true
}

defineExpose({ validateRules })
</script>

<template>
  <div style="width: 100%" class="function-CodemirrorEditor">
    <Codemirror
      v-bind="$attrs"
      ref="cmRef"
      v-model="modelValueProxy"
      :extensions="extensions"
      :style="codemirrorStyle"
      :tab-size="4"
      :autofocus="true"
    />
    <div class="function-CodemirrorEditor__format">
      <el-button text type="info" @click="format" class="magnify">
        <el-icon><DocumentChecked /></el-icon>
      </el-button>
    </div>
    <div class="function-CodemirrorEditor__footer">
      <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
        <MkIcon name="icon_magnify_outlined" style="font-size: 16px"></MkIcon>
      </el-button>
    </div>
    <!-- Codemirror 弹出层 -->
    <el-dialog v-model="dialogVisible" title="默认值" append-to-body fullscreen>
      <Codemirror
        v-model="cloneContent"
        :extensions="extensions"
        :style="codemirrorStyle"
        :tab-size="4"
        :autofocus="true"
        style="
          height: calc(100vh - 160px) !important;
          border: 1px solid #bbbfc4;
          border-radius: 4px;
        "
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<style lang="scss">
.function-CodemirrorEditor__footer {
  position: absolute;
  bottom: 10px;
  right: 10px;
}
.function-CodemirrorEditor {
  position: relative;
}
.function-CodemirrorEditor__format {
  position: absolute;
  top: 10px;
  right: 10px;
}
</style>
