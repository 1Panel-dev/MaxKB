<template>
  <el-dialog
    :title="$t('views.applicationOverview.appInfo.EmbedDialog.embedDialogTitle')"
    v-model="dialogVisible"
    width="900"
    class="embed-dialog"
  >
    <el-row :gutter="12">
      <el-col :span="12">
        <div class="border">
          <p class="title p-16 bold">
            {{ $t('views.applicationOverview.appInfo.EmbedDialog.fullscreenModeTitle') }}
          </p>
          <img src="@/assets/window1.png" alt="" class="ml-8" height="150" />
          <div class="code layout-bg border-t p-16">
            <div class="flex-between">
              <span class="bold">{{
                $t('views.applicationOverview.appInfo.EmbedDialog.copyInstructions')
              }}</span>
              <el-button text @click="copyClick(source1)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <div class="mt-8 pre-wrap">
              {{ source1 }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="border">
          <p class="title p-16 bold">
            {{ $t('views.applicationOverview.appInfo.EmbedDialog.floatingModeTitle') }}
          </p>
          <img src="@/assets/window2.png" alt="" class="ml-8" height="150" />
          <div class="code layout-bg border-t p-16">
            <div class="flex-between">
              <span class="bold">{{
                $t('views.applicationOverview.appInfo.EmbedDialog.copyInstructions')
              }}</span>
              <el-button text @click="copyClick(source2)">
                <AppIcon iconName="app-copy"></AppIcon>
              </el-button>
            </div>
            <div class="mt-8 pre-wrap">
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

const props = defineProps({
  data: Object
})

const emit = defineEmits(['addData'])

const dialogVisible = ref<boolean>(false)

const source1 = ref('')

const source2 = ref('')

const apiInputParams = ref([])

watch(dialogVisible, (bool) => {
  if (!bool) {
    source1.value = ''
    source2.value = ''
  }
})

const open = (val: string) => {
  source1.value = `<iframe
src="${application.location + val}?${mapToUrlParams(apiInputParams.value)}"
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
  )}&host=${window.location.host}&token=${val}&${mapToUrlParams(apiInputParams.value)}">
<\/script>
`
  dialogVisible.value = true
}

function mapToUrlParams(map: any[]) {
    const params = new URLSearchParams();

    map.forEach((item: any) => {
        params.append(encodeURIComponent(item.name), encodeURIComponent(item.value));
    });

    return params.toString(); // 返回 URL 查询字符串
}

watch(() => props.data,
  (val) => {
    if (val) {
      val.work_flow?.nodes
        ?.filter((v: any) => v.id === 'base-node')
        .map((v: any) => {
          apiInputParams.value = v.properties.input_field_list
            ? v.properties.input_field_list
              .filter((v: any) => v.assignment_method === 'api_input')
              .map((v: any) => {
                return {
                  name: v.variable,
                  value: v.default_value
                }
              })
            : []
        })
    }
  }
)

defineExpose({ open })
</script>
<style lang="scss" scope>
.embed-dialog {
  .title {
    color: var(--app-text-color) !important;
  }

  .code {
    color: var(--app-text-color) !important;

    font-weight: 400;
    font-size: 13px;
    white-space: pre;
    height: 180px;
  }
}
</style>
