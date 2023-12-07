<template>
  <div>
    <el-tooltip effect="dark" content="重新生成" placement="top">
      <el-button text @click="regeneration">
        <AppIcon iconName="VideoPlay"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip effect="dark" content="复制" placement="top">
      <el-button text @click="copyClick(data?.answer_text)">
        <AppIcon iconName="app-copy"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" />
    <el-tooltip
      effect="dark"
      content="赞同"
      placement="top"
      v-if="buttonData?.vote_status === '-1'"
    >
      <el-button text @click="voteHandle('0')" :disabled="loading">
        <AppIcon iconName="app-like"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      content="取消赞同"
      placement="top"
      v-if="buttonData?.vote_status === '0'"
    >
      <el-button text @click="voteHandle('-1')" :disabled="loading">
        <AppIcon iconName="app-like-color"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-divider direction="vertical" v-if="buttonData?.vote_status === '-1'" />
    <el-tooltip
      effect="dark"
      content="反对"
      placement="top"
      v-if="buttonData?.vote_status === '-1'"
    >
      <el-button text @click="voteHandle('1')" :disabled="loading">
        <AppIcon iconName="app-oppose"></AppIcon>
      </el-button>
    </el-tooltip>
    <el-tooltip
      effect="dark"
      content="取消反对"
      placement="top"
      v-if="buttonData?.vote_status === '1'"
    >
      <el-button text @click="voteHandle('-1')" :disabled="loading">
        <AppIcon iconName="app-oppose-color"></AppIcon>
      </el-button>
    </el-tooltip>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { copyClick } from '@/utils/clipboard'
import applicationApi from '@/api/application'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  applicationId: {
    type: String,
    default: ''
  },
  chartId: {
    type: String,
    default: ''
  },
  log: Boolean
})

const emit = defineEmits(['update:data', 'regeneration'])

const buttonData = ref(props.data)
const loading = ref(false)

function regeneration() {
  emit('regeneration')
}

function voteHandle(val: string) {
  applicationApi
    .putChatVote(props.applicationId, props.chartId, props.data.record_id, val, loading)
    .then((res) => {
      buttonData.value['vote_status'] = val
      emit('update:data', buttonData.value)
    })
}
</script>
<style lang="scss" scoped></style>
