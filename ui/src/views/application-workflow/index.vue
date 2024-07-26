<template>
  <div class="application-workflow" v-loading="loading">
    <div class="header border-b flex-between p-12-24">
      <div class="flex align-center">
        <back-button
          @click="router.push({ path: `/application/${id}/WORK_FLOW/overview` })"
        ></back-button>
        <h4>{{ detail?.name }}</h4>
        <el-text type="info" class="ml-16 color-secondary" v-if="saveTime"
          >保存时间：{{ datetimeFormat(saveTime) }}</el-text
        >
      </div>
      <div>
        <el-button icon="Plus" @click="showPopover = !showPopover" v-click-outside="clickoutside">
          添加组件
        </el-button>
        <el-button @click="clickShowDebug" :disabled="showDebug">
          <AppIcon iconName="app-play-outlined" class="mr-4"></AppIcon>
          调试</el-button
        >
        <el-button @click="saveApplication">
          <AppIcon iconName="app-save-outlined" class="mr-4"></AppIcon>
          保存
        </el-button>
        <el-button type="primary" @click="publicHandle"> 发布 </el-button>
      </div>
    </div>
    <!-- 下拉框 -->
    <el-collapse-transition>
      <div v-show="showPopover" class="workflow-dropdown-menu border border-r-4">
        <h5 class="title">基础组件</h5>
        <template v-for="(item, index) in menuNodes" :key="index">
          <div
            class="workflow-dropdown-item cursor flex p-8-12"
            @click="clickNodes(item)"
            @mousedown="onmousedown(item)"
          >
            <component :is="iconComponent(`${item.type}-icon`)" class="mr-8 mt-4" :size="32" />
            <div class="pre-line">
              <div class="lighter">{{ item.label }}</div>
              <el-text type="info" size="small">{{ item.text }}</el-text>
            </div>
          </div>
        </template>
      </div>
    </el-collapse-transition>
    <!-- 主画布 -->
    <div class="workflow-main">
      <workflow ref="workflowRef" v-if="detail" :data="detail?.work_flow" />
    </div>
    <!-- 调试 -->
    <el-collapse-transition>
      <div
        v-click-outside="clickoutsideDebug"
        class="workflow-debug-container"
        :class="enlarge ? 'enlarge' : ''"
        v-if="showDebug"
      >
        <div class="workflow-debug-header" :class="!isDefaultTheme ? 'custom-header' : ''">
          <div class="flex-between">
            <div class="flex align-center">
              <div class="mr-12 ml-24 flex">
                <AppAvatar
                  v-if="isAppIcon(detail?.icon)"
                  shape="square"
                  :size="32"
                  style="background: none"
                >
                  <img :src="detail?.icon" alt="" />
                </AppAvatar>
                <AppAvatar
                  v-else-if="detail?.name"
                  :name="detail?.name"
                  pinyinColor
                  shape="square"
                  :size="32"
                />
              </div>

              <h4>
                {{ detail?.name || $t('views.application.applicationForm.form.appName.label') }}
              </h4>
            </div>
            <div class="mr-16">
              <el-button link @click="enlarge = !enlarge">
                <AppIcon
                  :iconName="enlarge ? 'app-minify' : 'app-magnify'"
                  class="color-secondary"
                  style="font-size: 20px"
                ></AppIcon>
              </el-button>
              <el-button link @click="showDebug = false">
                <el-icon :size="20" class="color-secondary"><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        <div class="scrollbar-height">
          <AiChat :data="detail"></AiChat>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Workflow from '@/workflow/index.vue'
import { menuNodes } from '@/workflow/common/data'
import { iconComponent } from '@/workflow/icons/utils'
import applicationApi from '@/api/application'
import { isAppIcon } from '@/utils/application'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import useStore from '@/stores'
import { WorkFlowInstance } from '@/workflow/common/validate'

const { user, application } = useStore()
const router = useRouter()
const route = useRoute()

const isDefaultTheme = computed(() => {
  return user.isDefaultTheme()
})
const {
  params: { id }
} = route as any

let interval: any
const workflowRef = ref()

const loading = ref(false)
const detail = ref<any>(null)

const showPopover = ref(false)
const showDebug = ref(false)
const enlarge = ref(false)
const saveTime = ref<any>('')

function publicHandle() {
  workflowRef.value
    ?.validate()
    .then(() => {
      const obj = {
        work_flow: getGraphData()
      }
      applicationApi.putPublishApplication(id as String, obj, loading).then(() => {
        getDetail()
        MsgSuccess('发布成功')
      })
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(res.node.properties?.stepName + '节点 ' + err_message)
      } else {
        const keys = Object.keys(err_message)
        MsgError(node.properties?.stepName + '节点 ' + err_message[keys[0]]?.[0]?.message)
      }
    })
}

function clickoutside() {
  showPopover.value = false
}
const clickShowDebug = () => {
  workflowRef.value
    ?.validate()
    .then(() => {
      const graphData = getGraphData()
      const workflow = new WorkFlowInstance(graphData)
      try {
        workflow.is_valid()
        detail.value = {
          type: 'WORK_FLOW',
          ...workflow.get_base_node()?.properties.node_data,
          work_flow: getGraphData()
        }

        showDebug.value = true
      } catch (e: any) {
        MsgError(e.toString())
      }
    })
    .catch((res: any) => {
      const node = res.node
      const err_message = res.errMessage
      if (typeof err_message == 'string') {
        MsgError(res.node.properties?.stepName + '节点 ' + err_message)
      } else {
        const keys = Object.keys(err_message)
        MsgError(node.properties?.stepName + '节点 ' + err_message[keys[0]]?.[0]?.message)
      }
    })
}
function clickoutsideDebug() {
  showDebug.value = false
}

function clickNodes(item: any) {
  workflowRef.value?.addNode(item)
}

function onmousedown(item: any) {
  workflowRef.value?.onmousedown(item)
}

function getGraphData() {
  return workflowRef.value?.getGraphData()
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    res.data?.work_flow['nodes'].map((v: any) => {
      v['properties']['noRender'] = true
    })
    detail.value = res.data
    saveTime.value = res.data?.update_time
  })
}

function saveApplication() {
  const obj = {
    work_flow: getGraphData()
  }
  application.asyncPutApplication(id, obj).then((res) => {
    saveTime.value = new Date()
  })
}

/**
 * 定时保存
 */
const initInterval = () => {
  interval = setInterval(() => {
    saveApplication()
  }, 60000)
}

/**
 * 关闭定时
 */
const closeInterval = () => {
  if (interval) {
    clearInterval(interval)
  }
}

onMounted(() => {
  getDetail()
  // 初始化定时任务
  initInterval()
})

onBeforeUnmount(() => {
  // 清除定时任务
  closeInterval()
  workflowRef.value?.clearGraphData()
})
</script>
<style lang="scss">
.application-workflow {
  background: var(--app-layout-bg-color);
  height: 100%;
  .header {
    background: #ffffff;
  }
  .workflow-main {
    height: calc(100vh - 62px);
    box-sizing: border-box;
  }
  .workflow-dropdown-menu {
    -moz-user-select: none; /* Firefox */
    -webkit-user-select: none; /* WebKit内核 */
    -ms-user-select: none; /* IE10及以后 */
    -khtml-user-select: none; /* 早期浏览器 */
    -o-user-select: none; /* Opera */
    user-select: none; /* CSS3属性 */
    position: absolute;
    top: 49px;
    right: 90px;
    z-index: 99;
    width: 268px;
    box-shadow: 0px 4px 8px 0px var(--app-text-color-light-1);
    background: #ffffff;
    padding-bottom: 8px;

    .title {
      padding: 12px 12px 4px;
    }
    .workflow-dropdown-item {
      &:hover {
        background: var(--app-text-color-light-1);
      }
    }
  }
}

.workflow-debug-container {
  z-index: 2000;
  position: relative;
  border-radius: 8px;
  border: 1px solid #ffffff;
  background: linear-gradient(
      188deg,
      rgba(235, 241, 255, 0.2) 39.6%,
      rgba(231, 249, 255, 0.2) 94.3%
    ),
    #eff0f1;
  box-shadow: 0px 4px 8px 0px rgba(31, 35, 41, 0.1);
  position: fixed;
  bottom: 16px;
  right: 16px;
  overflow: hidden;
  width: 420px;
  height: 600px;
  .workflow-debug-header {
    background: var(--app-header-bg-color);
    height: var(--app-header-height);
    line-height: var(--app-header-height);
    box-sizing: border-box;
    border-bottom: 1px solid var(--el-border-color);
  }
  .scrollbar-height {
    height: calc(100% - var(--app-header-height) - 24px);
    padding-top: 24px;
  }
  &.enlarge {
    width: 50% !important;
    height: 100% !important;
    bottom: 0 !important;
    right: 0 !important;
  }
}
</style>
