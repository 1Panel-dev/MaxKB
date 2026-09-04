<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import { searchModeOptions } from '../../config'
import type { KnowledgeSearchSetting } from '../../types'
import SearchSettingDialog from './SearchSettingDialog.vue'

defineOptions({ name: 'SearchKnowledgeNodeSetting' })

const props = defineProps<{ setting: KnowledgeSearchSetting }>()
const emit = defineEmits<{ update: [setting: KnowledgeSearchSetting] }>()
const settingDialogRef = useTemplateRef<InstanceType<typeof SearchSettingDialog>>('settingDialogRef')
const settingRows = computed(() => [
  { label: '检索模式', value: searchModeOptions.find(({ value }) => value === props.setting.search_mode)?.label ?? props.setting.search_mode },
  { label: '相似度高于', value: props.setting.similarity.toFixed(3) },
  { label: '引用分段数 TOP', value: props.setting.top_n },
  { label: '最多引用字符数', value: props.setting.max_paragraph_char_number },
])
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full">
        <span>检索参数</span>
        <el-button link type="primary" title="参数设置" @click="settingDialogRef?.open(setting)"><MkIcon :icon="Setting" /></el-button>
      </div>
    </template>
    <dl class="grid w-full grid-cols-2 gap-y-1">
      <template v-for="row in settingRows" :key="row.label">
        <dt class="text-N600">{{ row.label }}</dt>
        <dd>{{ row.value }}</dd>
      </template>
    </dl>
  </el-form-item>
  <SearchSettingDialog ref="settingDialogRef" @submit="emit('update', $event)" />
</template>
