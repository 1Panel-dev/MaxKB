<template>
  <el-dialog title="嵌入第三方" v-model="dialogVisible" width="900" class="embed-dialog">
    <el-row :gutter="12">
      <el-col :span="12">
        <div class="border">
          <img src="@/assets/window1.png" alt="" />
          <div class="code border-t p-16">
            <div class="flex-between">
              <span class="bold">复制以下代码进行嵌入</span>
              <el-button text @click="copyClick(source1)">
                <AppIcon iconName="app-copy"></AppIcon>
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
              <el-button text @click="copyClick(source2)">
                <AppIcon iconName="app-copy"></AppIcon>
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
import { copyClick } from '@/utils/clipboard'
import useStore from '@/stores'

const { application } = useStore()

const emit = defineEmits(['addData'])

const dialogVisible = ref<boolean>(false)

const source1 = ref('')

const source2 = ref('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    source1.value = ''
    source2.value = ''
  }
})

const open = (val: string) => {
  source1.value = `<iframe 
src="${application.location + val}"
style="width: 100%; height: 100%;" 
frameborder="0" 
allow="microphone">
</iframe>
`
  source2.value = `<script> window.maxkbChatConfig = { 
  token: "${val}",
  host: "${window.location.host}"
 }
 <\/script>
<script src="${window.location.origin}/ui/embeb.js">
<\/script>
`
  dialogVisible.value = true
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
