<template>
  <el-dialog title="嵌入第三方" v-model="dialogVisible" width="900" class="embed-dialog">
    <el-row :gutter="12">
      <el-col :span="12">
        <div class="border">
          <img src="@/assets/window1.png" alt="" />
          <div class="code border-t p-16">
            <div class="flex-between">
              <span class="bold">复制以下代码进行嵌入</span>
              <el-button text>
                <el-icon style="font-size: 13px"><CopyDocument /></el-icon>
              </el-button>
            </div>
            <div class="mt-8">
              {{ source1 }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="border">
          <img src="@/assets/window2.png" alt="" />
          <div class="code border-t p-16">
            <div class="flex-between">
              <span class="bold">复制以下代码进行嵌入</span>
              <el-button text>
                <el-icon style="font-size: 13px"><CopyDocument /></el-icon>
              </el-button>
            </div>
            <div class="mt-8">
              {{ source2 }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array<any>,
    default: () => []
  }
})

const emit = defineEmits(['addData'])

const loading = ref(false)
const dialogVisible = ref<boolean>(false)
const source1 = ref(`<iframe 
src="https://udify.app/chatbot/ASkyzvhN5Z1h6k7g"
style="width: 100%; height: 100%;" 
frameborder="0" 
allow="microphone">
</iframe>
`)

const source2 = ref(`<script> window.difyChatbotConfig = { 
  token: '85FfbbzTpXzzr40X'
 }
 <\/script>
<script src="https://udify.app/embed.min.js"
 id="85FfbbzTpXzzr40X"
 defer>
<\/script>
`)

watch(dialogVisible, (bool) => {
  if (!bool) {
    loading.value = false
  }
})

const open = (checked: any) => {
  dialogVisible.value = true
}
const submitHandle = () => {
  dialogVisible.value = false
}

defineExpose({ open })
</script>
<style lang="scss" scope>
.embed-dialog {
  .code {
    color: var(--app-text-color) !important;
    background: var(--app-layout-bg-color);
    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 180px;
  }
}
</style>
