<script setup lang="ts">
import PythonCodeEditor from '@/components/codemirror-editor/python.vue'

defineOptions({ name: 'ToolCodeSetting' })

withDefaults(defineProps<{ showGenerate?: boolean }>(), { showGenerate: false })

const code = defineModel<string>({ required: true })
</script>

<template>
  <section>
    <div class="mb-4 flex-between">
      <div class="flex items-center gap-2">
        <h4 class="mk-title-decoration mk-required">工具内容（Python）</h4>
        <span class="text-N600">使用工具时不显示</span>
      </div>
      <!-- // TODO: 生成功能 -->
      <el-button v-if="showGenerate" link type="primary">
        <MkIcon name="icon_star" />
        <span>生成</span>
      </el-button>
    </div>

    <el-form-item prop="code">
      <PythonCodeEditor v-model="code" title="工具内容（Python）">
        <template v-if="showGenerate" #header-extra>
          <!-- // TODO: 生成功能 -->
          <el-button link type="primary">
            <MkIcon name="icon_star" />
            <span>生成</span>
          </el-button>
        </template>
      </PythonCodeEditor>
    </el-form-item>
  </section>
</template>
