<template>
  <el-dialog
    class="execution-details-dialog"
    title="执行详情"
    v-model="dialogVisible"
    destroy-on-close
    align-center
    @click.stop
  >
    <el-scrollbar>
      <div class="execution-details">
        <template v-for="(item, index) in arraySort(detail, 'index')" :key="index">
          <el-card class="mb-8" shadow="never" style="--el-card-padding: 12px 16px">
            <div class="flex-between cursor" @click="current = current === index ? '' : index">
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
                <span class="mr-16 color-secondary">{{ item?.run_time?.toFixed(2) || 0.0 }} s</span>
                <el-icon class="success" :size="16" v-if="item.status === 200"
                  ><CircleCheck
                /></el-icon>
                <el-icon class="danger" :size="16" v-else><CircleClose /></el-icon>
              </div>
            </div>
            <el-collapse-transition>
              <div class="mt-12" v-if="current === index">
                <template v-if="item.status === 200">
                  <!-- 开始 -->
                  <template v-if="item.type === WorkflowType.Start">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">参数输入</h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                  </template>
                  <!-- 知识库检索 -->
                  <template v-if="item.type == WorkflowType.SearchDataset">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">检索内容</h5>
                      <div class="p-8-12 border-t-dashed lighter">{{ item.question || '-' }}</div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">检索结果</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.paragraph_list?.length > 0">
                          <template
                            v-for="(paragraph, paragraphIndex) in arraySort(
                              item.paragraph_list,
                              'similarity',
                              true
                            )"
                            :key="paragraphIndex"
                          >
                            <ParagraphCard :data="paragraph" :index="paragraphIndex" />
                          </template>
                        </template>
                        <template v-else> - </template>
                      </div>
                    </div>
                  </template>
                  <!-- 判断器 -->
                  <template v-if="item.type == WorkflowType.Condition">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">判断结果</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.branch_name || '-' }}
                      </div>
                    </div>
                  </template>
                  <!-- AI 对话 / 问题优化-->
                  <template
                    v-if="item.type == WorkflowType.AiChat || item.type == WorkflowType.Question"
                  >
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">角色设定 (System)</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        {{ item.system || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">历史记录</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <template v-if="item.history_message?.length > 0">
                          <p
                            class="mt-4 mb-4"
                            v-for="(history, historyIndex) in item.history_message"
                            :key="historyIndex"
                          >
                            <span class="color-secondary mr-4">{{ history.role }}:</span
                            ><span>{{ history.content }}</span>
                          </p>
                        </template>
                        <template v-else> - </template>
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">本次对话</h5>
                      <div class="p-8-12 border-t-dashed lighter pre-line">
                        {{ item.question || '-' }}
                      </div>
                    </div>
                    <div class="card-never border-r-4 mt-8">
                      <h5 class="p-8-12">AI 回答</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <MdPreview
                          v-if="item.answer"
                          ref="editorRef"
                          editorId="preview-only"
                          :modelValue="item.answer"
                          style="background: none"
                        />
                        <template v-else> - </template>
                      </div>
                    </div>
                  </template>

                  <!-- 指定回复 -->
                  <template v-if="item.type === WorkflowType.Reply">
                    <div class="card-never border-r-4">
                      <h5 class="p-8-12">回复内容</h5>
                      <div class="p-8-12 border-t-dashed lighter">
                        <el-scrollbar height="150">
                          <MdPreview
                            v-if="item.answer"
                            ref="editorRef"
                            editorId="preview-only"
                            :modelValue="item.answer"
                            style="background: none"
                          />
                          <template v-else> - </template>
                        </el-scrollbar>
                      </div>
                    </div>
                  </template>
                </template>
                <template v-else>
                  <div class="card-never border-r-4">
                    <h5 class="p-8-12">错误日志</h5>
                    <div class="p-8-12 border-t-dashed lighter">{{ item.err_message || '-' }}</div>
                  </div>
                </template>
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
import ParagraphCard from './component/ParagraphCard.vue'
import { arraySort } from '@/utils/utils'
import { iconComponent } from '@/workflow/icons/utils'
import { WorkflowType } from '@/enums/workflow'

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
.execution-details-dialog {
  padding: 0;

  .el-dialog__header {
    padding: 24px 24px 0 24px;
  }
  .el-dialog__body {
    padding: 8px !important;
  }
  .execution-details {
    max-height: calc(100vh - 260px);
    .arrow-icon {
      transition: 0.2s;
    }
  }
}
@media only screen and (max-width: 768px) {
  .execution-details-dialog {
    width: 90% !important;
    .footer-content {
      display: block;
    }
  }
}
</style>
