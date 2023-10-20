<template>
  <!-- 外层div -->
  <div ref="InputTag" class="tags-input">
    <div class="tags-container" v-if="tagsList.length">
      <!-- 标签 -->
      <el-tag
        v-for="(item, index) in tagsList"
        :key="index"
        @close="removeTag(item)"
        closable
        class="mr-10"
        >{{ item }}
      </el-tag>
    </div>
    <!-- 输入框 -->
    <el-input
      :validate-event="false"
      v-model="currentval"
      :placeholder="tagsList.length == 0 ? placeholder : ''"
      @keydown.enter="addTags"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
defineOptions({ name: 'TagsInput' })
const props = defineProps({
  tags: {
    // 多个
    type: Array<String>,
    default: () => []
  },
  tag: {
    // 单个
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入'
  },
  limit: {
    // 最多生成标签数
    type: Number,
    default: -1
  },
  reg: {
    type: String,
    default: ''
  }
})
const emit = defineEmits(['update:tags', 'update:tag'])
const currentval = ref('')
const tagsList = ref<String[]>([])

watch([tagsList, currentval], (val) => {
  if (val[0]?.length > 0) {
    emit('update:tags', val[0])
  } else if (val[1]) {
    emit('update:tag', val[1])
  }
})

function addTags() {
  const val = currentval.value.trim()
  if (val) {
    tagsList.value.push(val)
  }
  currentval.value = ''
}
function removeTag(tag: String) {
  tagsList.value.splice(tagsList.value.indexOf(tag), 1)
}
</script>
<style lang="scss" scoped>
.tags-input {
  width: 100%;
  min-height: 70px;
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  :deep(.el-input__wrapper) {
    background: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    resize: none;
  }
  .tags-container {
    padding: 0 6px;
  }
}
</style>
