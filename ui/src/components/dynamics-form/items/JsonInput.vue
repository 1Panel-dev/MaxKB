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
        <el-icon><DocumentChecked /></el-icon
      ></el-button>
    </div>
    <div class="function-CodemirrorEditor__footer">
      <el-button text type="info" @click="openCodemirrorDialog" class="magnify">
        <AppIcon iconName="app-magnify" style="font-size: 16px"></AppIcon>
      </el-button>
    </div>
    <!-- Codemirror 弹出层 -->
    <el-dialog v-model="dialogVisible" title="Python 代码" append-to-body>
      <Codemirror
        v-model="cloneContent"
        :extensions="extensions"
        :style="codemirrorStyle"
        :tab-size="4"
        :autofocus="true"
        style="height: 300px !important; border: 1px solid #bbbfc4; border-radius: 4px"
      />
      <template #footer>
        <div class="dialog-footer mt-24">
          <el-button type="primary" @click="submitDialog"> 确认</el-button>
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
const props = withDefaults(defineProps<{ modelValue?: string }>(), { modelValue: '{}' })
const emit = defineEmits(['update:modelValue'])
const model_value = computed({
  get: () => {
    if (!props.modelValue) {
      emit('update:modelValue', '{}')
    }
    return props.modelValue
  },
  set: (v: string) => {
    if (!v) {
      emit('update:modelValue', '{}')
    } else {
      emit('update:modelValue', v)
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
