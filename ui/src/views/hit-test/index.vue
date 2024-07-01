<template>
  <div class="hit-test">
    <LayoutContainer>
      <template #header>
        <h4>
          命中测试
          <el-text type="info" class="ml-4">针对用户提问调试段落匹配情况，保障回答效果。</el-text>
        </h4>
      </template>
      <div class="hit-test__main p-16" v-loading="loading">
        <div class="question-title clearfix" v-if="questionTitle">
          <div class="avatar">
            <AppAvatar>
              <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
            </AppAvatar>
          </div>
          <div class="content">
            <h4 class="text break-all">{{ questionTitle }}</h4>
          </div>
        </div>
        <el-scrollbar>
          <div class="hit-test-height">
            <el-empty v-if="first" :image="emptyImg" description="命中段落显示在这里" />
            <el-empty v-else-if="paragraphDetail.length == 0" description="没有命中的分段" />
            <el-row v-else>
              <el-col
                :xs="24"
                :sm="12"
                :md="12"
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
                  class="document-card layout-bg layout-bg cursor"
                  :class="item.is_active ? '' : 'disabled'"
                  :showIcon="false"
                  @click="editParagraph(item)"
                >
                  <template #icon>
                    <AppAvatar class="mr-12 avatar-light" :size="22">
                      {{ index + 1 + '' }}</AppAvatar
                    >
                  </template>
                  <div class="active-button primary">{{ item.similarity?.toFixed(3) }}</div>
                  <template #footer>
                    <div class="footer-content flex-between">
                      <el-text>
                        <el-icon>
                          <Document />
                        </el-icon>
                        {{ item?.document_name }}
                      </el-text>
                      <div v-if="item.trample_num || item.star_num">
                        <span v-if="item.star_num">
                          <AppIcon iconName="app-like-color"></AppIcon>
                          {{ item.star_num }}
                        </span>
                        <span v-if="item.trample_num" class="ml-4">
                          <AppIcon iconName="app-oppose-color"></AppIcon>
                          {{ item.trample_num }}
                        </span>
                      </div>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </div>

      <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
    </LayoutContainer>
    <div class="hit-test__operate p-24 pt-0">
      <el-popover :visible="popoverVisible" placement="right-end" :width="500" trigger="click">
        <template #reference>
          <el-button icon="Setting" class="mb-8" @click="settingChange('open')">参数设置</el-button>
        </template>
        <div class="mb-16">
          <div class="title mb-8">检索模式</div>
          <el-radio-group
            v-model="cloneForm.search_mode"
            class="card__radio"
            @change="changeHandle"
          >
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'embedding' ? 'active' : ''"
            >
              <el-radio value="embedding" size="large">
                <p class="mb-4">向量检索</p>
                <el-text type="info">通过向量距离计算与用户问题最相似的文本分段</el-text>
              </el-radio>
            </el-card>
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'keywords' ? 'active' : ''"
            >
              <el-radio value="keywords" size="large">
                <p class="mb-4">全文检索</p>
                <el-text type="info">通过关键词检索，返回包含关键词最多的文本分段</el-text>
              </el-radio>
            </el-card>
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'blend' ? 'active' : ''"
            >
              <el-radio value="blend" size="large">
                <p class="mb-4">混合检索</p>
                <el-text type="info"
                  >同时执行全文检索和向量检索，再进行重排序，从两类查询结果中选择匹配用户问题的最佳结果</el-text
                >
              </el-radio>
            </el-card>
          </el-radio-group>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="mb-16">
              <div class="title mb-8">相似度高于</div>
              <el-input-number
                v-model="cloneForm.similarity"
                :min="0"
                :max="cloneForm.search_mode === 'blend' ? 2 : 1"
                :precision="3"
                :step="0.1"
                :value-on-clear="0"
                controls-position="right"
                class="w-full"
              />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="mb-16">
              <div class="title mb-8">返回分段数 TOP</div>
              <el-input-number
                v-model="cloneForm.top_number"
                :min="1"
                :max="100"
                controls-position="right"
                class="w-full"
              />
            </div>
          </el-col>
        </el-row>

        <div class="text-right">
          <el-button @click="popoverVisible = false">取消</el-button>
          <el-button type="primary" @click="settingChange('close')">确认</el-button>
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
import { cloneDeep } from 'lodash'
import datasetApi from '@/api/dataset'
import applicationApi from '@/api/application'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import { arraySort } from '@/utils/utils'
import emptyImg from '@/assets/hit-test-empty.png'

const route = useRoute()
const {
  meta: { activeMenu },
  params: { id }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const paragraphDetail = ref<any[]>([])
const title = ref('')
const inputValue = ref('')
const formInline = ref({
  similarity: 0.6,
  top_number: 5,
  search_mode: 'embedding'
})

// 第一次加载
const first = ref(true)

const cloneForm = ref<any>({})

const popoverVisible = ref(false)
const questionTitle = ref('')

const isDisabledChart = computed(() => !inputValue.value)

const isApplication = computed(() => {
  return activeMenu.includes('application')
})
const isDataset = computed(() => {
  return activeMenu.includes('dataset')
})

function changeHandle(val: string) {
  if (val === 'keywords') {
    cloneForm.value.similarity = 0
  } else {
    cloneForm.value.similarity = 0.6
  }
}

function settingChange(val: string) {
  if (val === 'open') {
    popoverVisible.value = true
    cloneForm.value = cloneDeep(formInline.value)
  } else if (val === 'close') {
    popoverVisible.value = false
    formInline.value = cloneDeep(cloneForm.value)
  }
}

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
    ...formInline.value
  }
  if (isDataset.value) {
    datasetApi.getDatasetHitTest(id, obj, loading).then((res) => {
      paragraphDetail.value = res.data && arraySort(res.data, 'comprehensive_score', true)
      questionTitle.value = inputValue.value
      inputValue.value = ''
      first.value = false
    })
  } else if (isApplication.value) {
    applicationApi.getApplicationHitTest(id, obj, loading).then((res) => {
      paragraphDetail.value = res.data && arraySort(res.data, 'comprehensive_score', true)
      questionTitle.value = inputValue.value
      inputValue.value = ''
      first.value = false
    })
  }
}

function refresh(data: any) {
  if (data) {
    const obj = paragraphDetail.value.filter((v) => v.id === data.id)[0]
    obj.content = data.content
    obj.title = data.title
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
