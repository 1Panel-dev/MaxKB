<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.embedInWebsite')"
    v-model="dialogVisible"
    width="900"
    class="embed-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-row :gutter="12">
      <el-col :span="8">
        <div class="border">
          <p class="title p-16 bold">
            {{ $t('views.applicationOverview.appInfo.EmbedDialog.fullscreenModeTitle') }}
          </p>
          <img src="@/assets/window1.png" alt="" class="ml-8" height="150" />
          <div class="code layout-bg border-t p-8">
            <div class="flex-between p-8">
              <span class="bold">{{
                $t('views.applicationOverview.appInfo.EmbedDialog.copyInstructions')
              }}</span>
              <el-button text @click="copyClick(source1)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <el-scrollbar height="150" always>
              <div class="pre-wrap p-8 pt-0">
                {{ source1 }}
              </div>
            </el-scrollbar>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="border">
          <p class="title p-16 bold">
            {{ $t('views.applicationOverview.appInfo.EmbedDialog.mobileModeTitle') }}
          </p>
          <img src="@/assets/window3.png" alt="" class="ml-8" height="150" />
          <div class="code layout-bg border-t p-8">
            <div class="flex-between p-8">
              <span class="bold">{{
                $t('views.applicationOverview.appInfo.EmbedDialog.copyInstructions')
              }}</span>
              <el-button text @click="copyClick(source3)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <el-scrollbar height="150" always>
              <div class="pre-wrap p-8 pt-0">
                {{ source3 }}
              </div>
            </el-scrollbar>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="border">
          <p class="title p-16 bold">
            {{ $t('views.applicationOverview.appInfo.EmbedDialog.floatingModeTitle') }}
          </p>
          <img src="@/assets/window2.png" alt="" class="ml-8" height="150" />
          <div class="code layout-bg border-t p-8">
            <div class="flex-between p-8">
              <span class="bold">{{
                $t('views.applicationOverview.appInfo.EmbedDialog.copyInstructions')
              }}</span>
              <el-button text @click="copyClick(source2)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <el-scrollbar height="150" always>
              <div class="pre-wrap p-8 pt-0">
                {{ source2 }}
              </div>
            </el-scrollbar>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { copyClick } from '@/utils/clipboard'
import useStore from '@/stores'

const { application } = useStore()

const props = defineProps({
  data: Object,
  apiInputParams: String
})

const emit = defineEmits(['addData'])

const dialogVisible = ref<boolean>(false)

const source1 = ref('')

const source2 = ref('')
const source3 = ref('')

const urlParams1 = computed(() => (props.apiInputParams ? '?' + props.apiInputParams : ''))
const urlParams2 = computed(() => (props.apiInputParams ? '&' + props.apiInputParams : ''))
const urlParams3 = computed(() =>
  props.apiInputParams ? '?mode=mobile&' + props.apiInputParams : '?mode=mobile'
)
watch(dialogVisible, (bool) => {
  if (!bool) {
    source1.value = ''
    source2.value = ''
    source3.value = ''
  }
})

const open = (val: string) => {
  source1.value = `<iframe
src="${application.location + val + urlParams1.value}"
style="width: 100%; height: 100%;"
frameborder="0"
allow="microphone">
</iframe>
`

  source2.value = `<script
async
defer
src="${window.location.origin}/api/application/embed?protocol=${window.location.protocol.replace(
    ':',
    ''
  )}&host=${window.location.host}&token=${val}${urlParams2.value}">
<\/script>
`
  source3.value = `<iframe
src="${application.location + val + urlParams3.value}"
style="width: 100%; height: 100%;"
frameborder="0"
allow="microphone">
</iframe>
`

  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss" scoped>
.embed-dialog {
  .title {
    color: var(--app-text-color) !important;
  }

  .code {
    color: var(--app-text-color) !important;

    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 188px;
  }
}
</style>
