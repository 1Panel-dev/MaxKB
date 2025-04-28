<template>
  <div style="width: 100%" class="function-CodemirrorEditor">
    <Codemirror
      v-bind="$attrs"
      ref="cmRef"
      v-model="model_value"
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
        <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
      </el-button>
    </div>
    <!-- Codemirror 弹出层 -->
    <el-dialog
      v-model="dialogVisible"
      :title="$t('dynamicsForm.default.label')"
      append-to-body
      fullscreen
    >
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
          <el-button type="primary" @click="submitDialog"> {{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { json, jsonParseLinter } from '@codemirror/lang-json'
import { oneDark } from '@codemirror/theme-one-dark'
import { Codemirror } from 'vue-codemirror'
import { linter } from '@codemirror/lint'
import { computed, ref } from 'vue'
import { t } from '@/locales'
const props = withDefaults(defineProps<{ modelValue?: any }>(), { modelValue: () => {} })
const emit = defineEmits(['update:modelValue'])

const cache_model_value_str = ref<string>()

const model_value = computed({
  get: () => {
    if (cache_model_value_str.value) {
      return cache_model_value_str.value
    }
    return JSON.stringify(props.modelValue, null, 4)
  },
  set: (v: string) => {
    if (!v) {
      emit('update:modelValue', JSON.parse('{}'))
    } else {
      try {
        cache_model_value_str.value = v
        const result = JSON.parse(v)
        emit('update:modelValue', result)
      } catch (e) {}
    }
  }
})

const extensions = [json(), linter(jsonParseLinter()), oneDark]

const codemirrorStyle = {
  height: '210px!important',
  width: '100%'
}

// 弹出框相关代码
const dialogVisible = ref<boolean>(false)

const cloneContent = ref<string>('')

const openCodemirrorDialog = () => {
  cloneContent.value = model_value.value
  dialogVisible.value = true
}

const format = () => {
  try {
    const json_str = JSON.parse(model_value.value)
    model_value.value = JSON.stringify(json_str, null, 4)
  } catch (e) {}
}

function submitDialog() {
  model_value.value = cloneContent.value
  dialogVisible.value = false
}
/**
 * 校验格式
 * @param rule
 * @param value
 * @param callback
 */
const validate_rules = (rule: any, value: any, callback: any) => {
  if (model_value.value) {
    try {
      JSON.parse(model_value.value)
    } catch (e) {
      callback(new Error(t('dynamicsForm.tip.requiredMessage')))
      return false
    }
  }
  return true
}

defineExpose({ validate_rules: validate_rules })
</script>
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
