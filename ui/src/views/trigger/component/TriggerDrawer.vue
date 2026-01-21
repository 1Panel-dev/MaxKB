<template>
  <el-drawer v-model="drawer" title="创建触发器">
    <el-form
      :model="form"
      label-width="auto"
      ref="triggerFormRef"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
    >
      <el-form-item
        label="触发器名称"
        prop="name"
        :rules="{
          message: `触发器名称为必填参数`,
          trigger: 'blur',
          required: true,
        }"
      >
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item
        label="描述"
        prop="desc"
        :rules="{
          message: `触发器名称为必填参数`,
          trigger: 'blur',
          required: true,
        }"
      >
        <el-input v-model="form.desc" />
      </el-form-item>
      <el-form-item
        label="触发器类型"
        prop="desc"
        :rules="{
          message: `触发器名称为必填参数`,
          trigger: 'blur',
          required: true,
        }"
      >
        <el-radio-group v-model="form.trigger_type" class="card__radio">
          <el-card
            shadow="never"
            class="mb-16"
            :class="form.trigger_type === 'SCHEDULED' ? 'active' : ''"
          >
            <el-radio value="SCHEDULED" size="large">
              <p class="mb-4">定时触发</p>
              <el-text type="info"> 每月、每周、每日或间隔时间执行任务</el-text>
            </el-radio>
            <el-card
              v-if="form.trigger_type === 'SCHEDULED'"
              shadow="never"
              class="card-never mt-16 w-full"
              style="margin-left: 30px"
              ><div>
                <el-row style="font-size: 14px" class="mb-8 w-full" :gutter="10">
                  <el-col :span="24" class="w-full">
                    <span s class="w-full">触发周期</span>
                  </el-col>
                </el-row>
                <el-row style="width: 100%" :gutter="10" class="mb-8">
                  <el-col :span="24">
                    <div class="grid-content ep-bg-purple" />
                    <el-cascader v-model="scheduled" :options="options" @change="handleChange" />
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-card>
          <el-card
            shadow="never"
            class="mb-16"
            :class="form.trigger_type === 'EVENT' ? 'active' : ''"
          >
            <el-radio value="EVENT" size="large">
              <p class="mb-4">事件触发</p>
              <el-text type="info"> 当某个事件发送时执行任务 </el-text>
            </el-radio>

            <el-card
              v-if="form.trigger_type === 'EVENT'"
              shadow="never"
              class="card-never mt-16"
              style="margin-left: 30px"
            >
              <el-form-item label="复制 URL 到你的应用">
                <el-input v-bind:modelValue="event_url">
                  <template #append>
                    <el-button @click="copy" :icon="CopyDocument" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="Bearer Token">
                <el-input v-model="form.trigger_setting.token"> </el-input>
              </el-form-item>
              <el-form-item label="请求参数">
                <template #label>
                  <div class="flex-between">
                    {{ $t('dynamicsForm.Select.label') }}
                    <el-button link type="primary" @click.stop="addParameter()">
                      <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                      {{ $t('common.add') }}
                    </el-button>
                  </div>
                </template>
                <el-card class="w-full">
                  <el-row style="width: 100%" :gutter="10">
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      参数名
                    </el-col>
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      类型
                    </el-col>
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      描述
                    </el-col>
                    <el-col :span="6">
                      <div class="grid-content ep-bg-purple" />
                      必填
                    </el-col>
                  </el-row>
                  <el-row
                    style="width: 100%"
                    v-for="(option, $index) in form.trigger_setting.body"
                    :key="$index"
                    :gutter="10"
                    class="mb-8"
                  >
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      <el-input
                        v-model="form.trigger_setting.body[$index].field"
                        :placeholder="$t('dynamicsForm.tag.placeholder')"
                      />
                    </el-col>
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      <el-select
                        v-model="form.trigger_setting.body[$index].type"
                        placeholder="请选择类型"
                      >
                        <el-option label="string" value="string" />
                        <el-option label="int" value="int" />
                        <el-option label="dict" value="dict" />
                        <el-option label="array" value="array" />
                        <el-option label="float" value="float" />
                        <el-option label="boolean" value="boolean" />
                      </el-select>
                    </el-col>
                    <el-col :span="5">
                      <div class="grid-content ep-bg-purple" />
                      <el-input
                        v-model="form.trigger_setting.body[$index].desc"
                        :placeholder="$t('dynamicsForm.Select.label')"
                      />
                    </el-col>
                    <el-col :span="6">
                      <div class="grid-content ep-bg-purple" />
                      <el-switch
                        v-model="form.trigger_setting.body[$index].required"
                        size="small"
                      />
                    </el-col>
                    <el-col :span="1">
                      <div class="grid-content ep-bg-purple" />
                      <el-button link class="ml-8" @click.stop="delParameter($index)">
                        <AppIcon iconName="app-delete"></AppIcon>
                      </el-button>
                    </el-col>
                  </el-row>
                </el-card>
              </el-form-item>
            </el-card>
          </el-card>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="任务执行">
        <el-card shadow="never" class="card-never mt-16 w-full" style="margin-left: 30px">
          <el-form-item label="智能体">
            <template #label>
              <div class="flex-between">
                智能体
                <el-button link type="primary" @click.stop="openApplicationDialog()">
                  <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                  {{ $t('common.add') }}
                </el-button>
              </div>
            </template>
            <el-card v-for="task in applicationTask" class="w-full">
              <el-collapse accordion>
                <el-collapse-item :title="applicationDetailsDict[task.source_id]?.name">
                  <ApplicationParameter
                    ref="applicationParameterRef"
                    v-if="applicationDetailsDict[task.source_id]"
                    :application="applicationDetailsDict[task.source_id]"
                    :trigger="form"
                    v-model="task.parameter"
                  ></ApplicationParameter>
                </el-collapse-item>
              </el-collapse>
            </el-card>
          </el-form-item>
        </el-card>
        <el-card shadow="never" class="card-never mt-16 w-full" style="margin-left: 30px">
          <el-form-item label="工具">
            <template #label>
              <div class="flex-between">
                工具
                <el-button link type="primary" @click.stop="openToolDialog()">
                  <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                  {{ $t('common.add') }}
                </el-button>
              </div>
            </template>
            <el-card v-for="task in toolTask" class="w-full">
              <el-collapse accordion>
                <el-collapse-item :title="toolDetailsDict[task.source_id]?.name">
                  <ToolParameter
                    ref="toolParameterRef"
                    v-if="toolDetailsDict[task.source_id]"
                    :tool="toolDetailsDict[task.source_id]"
                    :trigger="form"
                    v-model="task.parameter"
                  ></ToolParameter>
                </el-collapse-item>
              </el-collapse>
            </el-card> </el-form-item
        ></el-card>
      </el-form-item>
    </el-form>
    <ApplicationDialog @refresh="applicationRefresh" ref="applicationDialogRef"></ApplicationDialog>
    <ToolDialog @refresh="toolRefresh" ref="toolDialogRef"></ToolDialog>
    <template #footer>
      <el-form-item>
        <el-button type="primary" @click="submit">创建</el-button>
        <el-button @click="close">取消</el-button>
      </el-form-item>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { v4 as uuidv4 } from 'uuid'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CopyDocument } from '@element-plus/icons-vue'
import { copyClick } from '@/utils/clipboard'
import ApplicationDialog from '@/views/application/component/ApplicationDialog.vue'
import ToolDialog from '@/views/application/component/ToolDialog.vue'
import applicationAPI from '@/api/application/application'
import triggerAPI from '@/api/trigger/trigger'
import toolAPI from '@/api/tool/tool'
import ToolParameter from './ToolParameter.vue'
import ApplicationParameter from './ApplicationParameter.vue'
import { FormInstance } from 'element-plus'
const emit = defineEmits(['refresh'])
const triggerFormRef = ref<FormInstance>()
const copy = () => {
  copyClick(event_url.value)
}
const addParameter = () => {
  form.value.trigger_setting.body.push({ field: '', type: '' })
}
const delParameter = (index: number) => {
  form.value.trigger_setting.body.splice(index, 1)
}
const handleChange = (v: Array<any>) => {
  scheduled.value = v
}
const applicationDetailsDict = ref<any>({})
const toolDetailsDict = ref<any>({})
const applicationRefresh = (application_selected: any) => {
  const application_list: Array<any> = application_selected.application_ids
  const existApplicationIds = Object.keys(applicationDetailsDict)
  application_list
    .filter((id) => !existApplicationIds.includes(id))
    .map((id) => {
      return applicationAPI.getApplicationDetail(id).then((ok) => {
        applicationDetailsDict.value[ok.data.id] = ok.data
      })
    })
  const task_source_id_list = form.value.trigger_task
    .filter((task: any) => task.source_type === 'APPLICATION')
    .map((task: any) => task.source_id)

  application_list
    .filter((id) => !task_source_id_list.includes(id))
    .forEach((id) => {
      form.value.trigger_task.push({
        source_type: 'APPLICATION',
        source_id: id,
        is_active: false,
        parameter: {},
      })
    })
}
const applicationTask = computed(() => {
  return form.value.trigger_task.filter((task: any) => task.source_type === 'APPLICATION')
})
const toolTask = computed(() => {
  return form.value.trigger_task.filter((task: any) => task.source_type === 'TOOL')
})
const applicationParameterRef = ref<Array<InstanceType<typeof ApplicationParameter>>>()
const toolParameterRef = ref<Array<InstanceType<typeof ToolParameter>>>()
const toolRefresh = (tool_selected: any) => {
  const tool_ids: Array<any> = tool_selected.tool_ids

  const existToolIds = Object.keys(toolDetailsDict)
  tool_ids
    .filter((id) => !existToolIds.includes(id))
    .map((id) => {
      toolAPI.getToolById(id).then((ok) => {
        toolDetailsDict.value[ok.data.id] = ok.data
      })
    })
  const task_source_id_list = form.value.trigger_task
    .filter((task: any) => task.source_type === 'TOOL')
    .map((task: any) => task.source_id)
  tool_ids
    .filter((id) => !task_source_id_list.includes(id))
    .forEach((id) => {
      form.value.trigger_task.push({
        source_type: 'TOOL',
        source_id: id,
        is_active: false,
        parameter: {},
      })
    })
}

const applicationDialogRef = ref<InstanceType<typeof ApplicationDialog>>()
const toolDialogRef = ref<InstanceType<typeof ToolDialog>>()
const openApplicationDialog = () => {
  const application_id_list = form.value.trigger_task
    .filter((task: any) => task.source_type === 'APPLICATION')
    .map((task: any) => task.source_id)
  applicationDialogRef.value?.open(application_id_list)
}
const openToolDialog = () => {
  const tool_id_list = form.value.trigger_task
    .filter((task: any) => task.source_type === 'TOOL')
    .map((task: any) => task.source_id)
  toolDialogRef.value?.open(tool_id_list)
}
const drawer = ref<boolean>(false)
const times = Array.from({ length: 24 }, (_, i) => {
  const t = i.toString().padStart(2, '0') + ':00'
  return { label: t, value: t }
})
const days = Array.from({ length: 31 }, (_, i) => {
  const t = i.toString() + '日'
  return { label: t, value: i, children: times }
})
const hours = Array.from({ length: 24 }, (_, i) => {
  const t = i.toString().padStart(2, '0')
  return { label: t, value: i }
})
const minutes = Array.from({ length: 60 }, (_, i) => {
  const t = i.toString().padStart(2, '0')
  return { label: t, value: i }
})

const options = [
  {
    value: 'daily',
    label: '每日触发',
    multiple: true,
    children: times,
  },
  {
    value: 'weekly',
    label: '每周触发',
    children: [
      { label: '周日', value: 7, children: times },
      { label: '周一', value: 1, children: times },
      { label: '周二', value: 2, children: times },
      { label: '周三', value: 3, children: times },
      { label: '周四', value: 4, children: times },
      { label: '周五', value: 5, children: times },
      { label: '周六', value: 6, children: times },
    ],
  },
  { value: 'monthly', label: '每月触发', children: days },
  {
    value: 'interval',
    label: '间隔触发',
    children: [
      { label: '小时', value: 'hours', children: hours },
      { label: '分钟', value: 'minutes', children: minutes },
    ],
  },
]
const scheduled = computed({
  get: () => {
    const schedule_type = form.value.trigger_setting.schedule_type
    if (schedule_type) {
      if (schedule_type === 'interval') {
        const interval_value = form.value.trigger_setting.interval_value
        const interval_unit = form.value.trigger_setting.interval_unit
        return [schedule_type, interval_value, interval_unit].filter((item) => item !== undefined)
      } else {
        const days = form.value.trigger_setting.days
          ? form.value.trigger_setting.days[0]
          : undefined
        const time = form.value.trigger_setting.time
          ? form.value.trigger_setting.time[0]
          : undefined
        if (schedule_type == 'daily') {
          return [schedule_type, time].filter((item) => item !== undefined)
        }
        return [schedule_type, days, time].filter((item) => item !== undefined)
      }
    }
    return []
  },
  set: (value) => {
    const schedule_type = value[0]
    form.value.trigger_setting.schedule_type = schedule_type
    if (schedule_type == 'interval') {
      form.value.trigger_setting.interval_value = value[1]
      form.value.trigger_setting.interval_unit = value[2]
    } else {
      if (schedule_type == 'daily') {
        form.value.trigger_setting.time = [value[1]]
      } else {
        form.value.trigger_setting.days = [value[1]]
        form.value.trigger_setting.time = [value[2]]
      }
    }
  },
})
const getDefaultValue = () => {
  return {
    id: uuidv4(),
    name: '',
    desc: '',
    trigger_task: [],
    trigger_type: 'SCHEDULED',
    trigger_setting: {
      token: '',
      body: [],
    },
  }
}

const form = ref<any>(getDefaultValue())
const is_edit = ref<boolean>(false)
const event_url = computed(() => {
  return `${window.origin}${window.MaxKB.prefix}/api/trigger/v1/webhook/${form.value.id}`
})

const init = (trigger_id: string) => {
  triggerAPI.getTriggerDetail(trigger_id).then((ok) => {
    form.value = ok.data

    applicationDetailsDict.value = ok.data.application_task_list
      .map((item: any) => ({ [item.id]: item }))
      .reduce((x: any, y: any) => ({ ...x, ...y }), {})
    toolDetailsDict.value = ok.data.tool_task_list
      .map((item: any) => ({ [item.id]: item }))
      .reduce((x: any, y: any) => ({ ...x, ...y }), {})
  })
}

const open = (trigger_id?: string) => {
  is_edit.value = trigger_id ? true : false
  drawer.value = true
  if (trigger_id) {
    init(trigger_id)
  }
}

const close = () => {
  drawer.value = false
  form.value = getDefaultValue()
}
const submit = () => {
  Promise.all([
    ...(toolParameterRef.value ? toolParameterRef.value.map((item) => item.validate()) : []),
    ...(applicationParameterRef.value
      ? applicationParameterRef.value.map((item) => item.validate())
      : []),
    triggerFormRef.value?.validate(),
  ]).then((ok) => {
    triggerAPI.postTrigger(form.value).then((ok) => {
      close()
      emit('refresh')
    })
  })
}
onMounted(() => {})
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
