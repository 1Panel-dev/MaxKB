<template>
  <div class="hit-test">
    <LayoutContainer>
      <template #header>
        <h3>
          命中测试
          <el-text type="info" class="ml-4">针对用户提问调试段落匹配情况，保障回答效果。</el-text>
        </h3>
      </template>
      <div class="hit-test__main p-16" v-loading="loading">
        <div class="question-title clearfix">
          <div class="avatar">
            <AppAvatar>
              <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
            </AppAvatar>
          </div>
          <div class="content">
            <h4 class="text break-all">111111</h4>
          </div>
        </div>
        <el-scrollbar>
          <div class="hit-test-height">
            <el-empty v-if="paragraphDetail.length == 0" description="暂无数据" />
            <el-row v-else>
              <el-col
                :xs="24"
                :sm="12"
                :md="8"
                :lg="8"
                :xl="6"
                v-for="(item, index) in paragraphDetail"
                :key="index"
                class="p-8"
              >
                <CardBox
                  shadow="hover"
                  :title="item.title || '-'"
                  :description="item.content"
                  class="document-card cursor"
                  :class="item.is_active ? '' : 'disabled'"
                  :showIcon="false"
                  @click="editParagraph(item)"
                >
                  <template #footer>
                    <div class="footer-content flex-between">
                      <span> {{ numberFormat(item?.content.length) || 0 }} 个 字符 </span>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </div>

      <!-- <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" /> -->
    </LayoutContainer>
    <div class="hit-test__operate p-24 pt-0">
      <el-popover :visible="popoverVisible" placement="top-start" :width="560" trigger="click">
        <template #reference>
          <el-button icon="Setting" class="mb-8" @click="popoverVisible = !popoverVisible"
            >参数设置</el-button
          >
        </template>
        <div class="flex">
          <div>
            相似度
            <el-input-number
              v-model="formInline.similarity"
              :min="1"
              :max="100"
              controls-position="right"
              style="width: 100px"
            />
            %
          </div>

          <div class="ml-16">
            返回 Top
            <el-input-number
              v-model="formInline.top_number"
              :min="1"
              :max="10"
              controls-position="right"
              style="width: 100px"
            />
            个分段
          </div>
          <el-button class="ml-16" @click="popoverVisible = false">取消</el-button>
          <el-button type="primary" @click="popoverVisible = false">确认</el-button>
        </div>
      </el-popover>
      <div class="operate-textarea flex">
        <el-input
          ref="quickInputRef"
          v-model="inputValue"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 1, maxRows: 8 }"
          @keydown.enter="sendChatHandle($event)"
        />
        <div class="operate">
          <el-button
            text
            class="sent-button"
            :disabled="isDisabledChart || loading"
            @click="sendChatHandle"
          >
            <img v-show="isDisabledChart || loading" src="@/assets/icon_send.svg" alt="" />
            <img
              v-show="!isDisabledChart && !loading"
              src="@/assets/icon_send_colorful.svg"
              alt=""
            />
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import documentApi from '@/api/document'
import paragraphApi from '@/api/paragraph'
import datasetApi from '@/api/dataset'
// import ParagraphDialog from './component/ParagraphDialog.vue'
import { numberFormat } from '@/utils/utils'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'
const { paragraph } = useStore()
const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const paragraphDetail = ref<any[]>([])
const title = ref('')
const inputValue = ref('')
const formInline = reactive({
  similarity: 60,
  top_number: 5
})
const popoverVisible = ref(false)

const isDisabledChart = computed(() => !inputValue.value)

function editParagraph(row: any) {
  title.value = '分段详情'
  ParagraphDialogRef.value.open(row)
}

function sendChatHandle(event: any) {
  if (!event.ctrlKey) {
    // 如果没有按下组合键ctrl，则会阻止默认事件
    event.preventDefault()
    if (!isDisabledChart.value && !loading.value) {
      getHitTestList()
    }
  } else {
    // 如果同时按下ctrl+回车键，则会换行
    inputValue.value += '\n'
  }
}
function getHitTestList() {
  const obj = {
    query_text: inputValue.value,
    similarity: formInline.similarity / 100,
    top_number: formInline.top_number
  }
  datasetApi.getDatasetHitTest(id, obj, loading).then((res) => {
    paragraphDetail.value = res.data
  })
}

function refresh(data: any) {
  if (data) {
    const index = paragraphDetail.value.findIndex((v) => v.id === data.id)
    paragraphDetail.value.splice(index, 1, data)
  } else {
    paragraphDetail.value = []
    getHitTestList()
  }
}

onMounted(() => {})
</script>
<style lang="scss" scoped>
.hit-test {
  .question-title {
    .avatar {
      float: left;
    }
    .content {
      padding-left: 40px;
      .text {
        padding: 6px 0;
      }
    }
  }

  &__operate {
    .operate-textarea {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      :deep(.el-textarea__inner) {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 12px 16px;
      }
      .operate {
        padding: 6px 10px;
        .sent-button {
          max-height: none;
          .el-icon {
            font-size: 24px;
          }
        }
        :deep(.el-loading-spinner) {
          margin-top: -15px;
          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }
  }
}
.hit-test {
  &__header {
    position: absolute;
    right: calc(var(--app-base-px) * 3);
  }

  .hit-test-height {
    height: calc(var(--app-main-height) - 170px);
  }
  .document-card {
    height: 210px;
    background: var(--app-layout-bg-color);
    border: 1px solid var(--app-layout-bg-color);
    &:hover {
      background: #ffffff;
      border: 1px solid var(--el-border-color);
    }
    &.disabled {
      background: var(--app-layout-bg-color);
      border: 1px solid var(--app-layout-bg-color);
      :deep(.description) {
        color: var(--app-border-color-dark);
      }
      :deep(.title) {
        color: var(--app-border-color-dark);
      }
    }
    :deep(.description) {
      -webkit-line-clamp: 5 !important;
      height: 110px;
    }
    .active-button {
      position: absolute;
      right: 16px;
      top: 16px;
    }
  }
}
</style>
