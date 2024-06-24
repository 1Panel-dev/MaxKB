<template>
  <el-dialog title="执行详情" v-model="dialogVisible" destroy-on-close align-center @click.stop>
    <el-scrollbar>
      <div class="execution-details">
        <template v-for="(item, index) in arraySort(detail, 'index')" :key="index">
          <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
            <div class="flex-between cursor" @click="current = index">
              <div class="flex align-center">
                <el-icon class="mr-8 arrow-icon" :class="current === index ? 'rotate-90' : ''"
                  ><CaretRight
                /></el-icon>
                <component :is="iconComponent(`${item.type}-icon`)" class="mr-8" :size="24" />
                <h4>{{ item.name }}</h4>
              </div>
              <div class="flex align-center">
                <span
                  class="mr-16 color-secondary"
                  v-if="item.type === WorkflowType.Question || item.type === WorkflowType.AiChat"
                  >{{ item?.message_tokens + item?.answer_tokens }} tokens</span
                >
                <span class="mr-16 color-secondary">{{ item?.run_time?.toFixed(2) }} s</span>
                <el-icon class="success" :size="16"><CircleCheck /></el-icon>
              </div>
            </div>
            <el-collapse-transition>
              <div class="card-never border-r-4 mt-8" v-if="current === index">
                <h5 class="p-8-12">参数输入</h5>
                <div class="p-8-12 border-t-dashed lighter">如何快速开始</div>
              </div>
            </el-collapse-transition>
          </el-card>
        </template>
      </div>
    </el-scrollbar>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { cloneDeep } from 'lodash'
import { arraySort } from '@/utils/utils'
import { iconComponent } from '@/workflow/icons/utils'
import { WorkflowType } from '@/enums/workflow'
import { MdPreview } from 'md-editor-v3'

const dialogVisible = ref(false)
const detail = ref<any[]>([])

const current = ref<number | string>('')

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = []
  }
})

const open = (data: any) => {
  detail.value = cloneDeep(data)

  dialogVisible.value = true
}
onBeforeUnmount(() => {
  dialogVisible.value = false
})
defineExpose({ open })
</script>
<style lang="scss">
.execution-details {
  max-height: calc(100vh - 260px);
  .arrow-icon {
    transition: 0.2s;
  }
}
</style>
