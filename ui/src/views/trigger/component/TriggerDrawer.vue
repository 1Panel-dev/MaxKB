<template>
  <el-drawer
    v-model="drawer"
    :title="is_edit ? $t('views.trigger.editTrigger') : $t('views.trigger.createTrigger')"
    size="600"
    append-to-body
  >
    <el-form
      :model="form"
      label-width="auto"
      ref="triggerFormRef"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
    >
      <el-form-item
        :label="$t('views.trigger.from.triggerName.label')"
        prop="name"
        :rules="{
          message: $t('views.trigger.from.triggerName.requiredMessage'),
          trigger: 'blur',
          required: true,
        }"
      >
        <el-input
          v-model="form.name"
          maxlength="64"
          :placeholder="$t('views.trigger.from.triggerName.placeholder')"
          show-word-limit
          @blur="form.name = form.name?.trim()"
        />
      </el-form-item>
      <el-form-item
        :label="$t('common.desc')"
        prop="desc"
        :rules="{
          message: $t('common.inputPlaceholder'),
          trigger: 'blur',
          required: true,
        }"
      >
        <el-input
          v-model="form.desc"
          type="textarea"
          :placeholder="$t('common.inputPlaceholder')"
          :rows="3"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item
        :label="$t('common.type')"
        prop="trigger_type"
        :rules="{
          message: $t('common.selectPlaceholder'),
          trigger: 'blur',
          required: true,
        }"
      >
        <el-card
          shadow="never"
          class="mb-16 w-full cursor"
          :class="form.trigger_type === 'SCHEDULED' ? 'border-active' : ''"
          @click="form.trigger_type = 'SCHEDULED'"
        >
          <div class="flex align-center line-height-22">
            <el-avatar shape="square" :size="32">
              <img src="@/assets/trigger/icon_scheduled.svg" style="width: 58%" alt="" />
            </el-avatar>
            <div class="ml-12">
              <h5>{{ $t('views.trigger.type.scheduled') }}</h5>
              <el-text type="info" class="color-secondary font-small">{{
                $t('views.trigger.type.scheduledDesc')
              }}</el-text>
            </div>
          </div>

          <el-card
            v-if="form.trigger_type === 'SCHEDULED'"
            shadow="never"
            class="card-never mt-16 w-full"
            ><div>
              <el-row style="font-size: 14px" class="mb-8 w-full" :gutter="10">
                <el-col :span="24" class="w-full">
                  <span class="w-full">{{ $t('views.trigger.triggerCycle.title') }}</span>
                </el-col>
              </el-row>
              <el-row style="width: 100%" :gutter="10" class="mb-8">
                <el-col :span="24">
                  <el-cascader v-model="scheduled" :options="options" @change="handleChange" />
                </el-col>
              </el-row>
            </div>
          </el-card>
        </el-card>
        <el-card
          shadow="never"
          class="w-full cursor"
          :class="form.trigger_type === 'EVENT' ? 'border-active' : ''"
          @click="form.trigger_type = 'EVENT'"
        >
          <div class="flex align-center line-height-22">
            <el-avatar shape="square" class="avatar-orange" :size="32">
              <img src="@/assets/trigger/icon_event.svg" style="width: 58%" alt="" />
            </el-avatar>
            <div class="ml-12">
              <h5>{{ $t('views.trigger.type.event') }}</h5>
              <el-text type="info" class="color-secondary font-small">{{
                $t('views.trigger.type.eventDesc')
              }}</el-text>
            </div>
          </div>
          <el-card v-if="form.trigger_type === 'EVENT'" shadow="never" class="card-never mt-16">
            <el-form-item :label="$t('views.trigger.from.event_url.label')">
              <div class="complex-input flex align-center w-full" style="background-color: #ffffff">
                <el-input class="complex-input__left" v-bind:modelValue="event_url"></el-input>

                <el-tooltip :content="$t('common.copy')" placement="top">
                  <el-button text @click="copy">
                    <AppIcon iconName="app-copy" class="color-secondary"></AppIcon>
                  </el-button>
                </el-tooltip>
              </div>
            </el-form-item>
            <el-form-item label="Bearer Token">
              <el-input
                type="password"
                :placeholder="$t('common.inputPlaceholder')"
                v-model="form.trigger_setting.token"
                show-password
              >
              </el-input>
            </el-form-item>
            <el-form-item>
              <template #label>
                <div class="flex-between">
                  {{ $t('views.trigger.requestParameter') }}
                  <el-button link type="primary" @click.stop="addParameter()">
                    <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
                  </el-button>
                </div>
              </template>
              <el-card
                class="w-full border-none"
                shadow="never"
                style="--el-card-padding: 8px 16px 16px"
              >
                <el-row style="width: 100%" :gutter="10">
                  <el-col :span="7">
                    {{ $t('views.tool.form.paramName.label') }}
                  </el-col>
                  <el-col :span="7">
                    {{ $t('common.type') }}
                  </el-col>
                  <el-col :span="7">
                    {{ $t('common.desc') }}
                  </el-col>
                  <el-col :span="3">
                    {{ $t('common.required') }}
                  </el-col>
                </el-row>
                <el-row
                  style="width: 99%"
                  v-for="(option, $index) in form.trigger_setting.body"
                  :key="$index"
                  :gutter="8"
                >
                  <el-col :span="7" class="mb-8">
                    <el-input
                      v-model="form.trigger_setting.body[$index].field"
                      :placeholder="$t('common.inputPlaceholder')"
                    />
                  </el-col>
                  <el-col :span="7">
                    <el-select
                      v-model="form.trigger_setting.body[$index].type"
                      :placeholder="$t('common.selectPlaceholder')"
                    >
                      <el-option label="string" value="string" />
                      <el-option label="int" value="int" />
                      <el-option label="dict" value="dict" />
                      <el-option label="array" value="array" />
                      <el-option label="float" value="float" />
                      <el-option label="boolean" value="boolean" />
                    </el-select>
                  </el-col>
                  <el-col :span="7">
                    <el-input
                      v-model="form.trigger_setting.body[$index].desc"
                      :placeholder="$t('common.inputPlaceholder')"
                    />
                  </el-col>
                  <el-col :span="2">
                    <el-switch v-model="form.trigger_setting.body[$index].required" size="small" />
                  </el-col>
                  <el-col :span="1">
                    <el-button text class="ml-8" @click.stop="delParameter($index)">
                      <AppIcon iconName="app-delete" class="color-secondary"></AppIcon>
                    </el-button>
                  </el-col>
                </el-row>
              </el-card>
            </el-form-item>
          </el-card>
        </el-card>
      </el-form-item>
      <el-form-item :label="$t('views.trigger.taskExecution')">
        <template v-if="['APPLICATION', 'TOOL'].includes(resourceType)">
          <!-- 资源端智能体 -->
          <div class="w-full" v-if="resourceType === 'APPLICATION'">
            <template v-for="(item, index) in applicationTask" :key="index">
              <div class="border border-r-6 white-bg" style="padding: 2px 8px">
                <div class="flex-between">
                  <div class="flex align-center" style="line-height: 20px">
                    <el-avatar
                      v-if="applicationDetailsDict[item.source_id]?.icon"
                      shape="square"
                      :size="20"
                      style="background: none"
                      class="mr-8"
                    >
                      <img :src="resetUrl(applicationDetailsDict[item.source_id]?.icon)" alt="" />
                    </el-avatar>
                    <AppIcon v-else class="mr-8" :size="20" />

                    <div class="ellipsis-1" :title="applicationDetailsDict[item.source_id]?.name">
                      {{ applicationDetailsDict[item.source_id]?.name }}
                    </div>
                  </div>
                  <div style="margin-top: -2px">
                    <span class="mr-4">
                      <el-button
                        text
                        @click="showTast = showTast === 'agent' + index ? '' : 'agent' + index"
                      >
                        <el-icon
                          class="arrow-icon"
                          :class="showTast === 'agent' + index ? 'rotate-180' : ''"
                        >
                          <ArrowDown />
                        </el-icon>
                      </el-button>
                    </span>
                  </div>
                </div>
                <ApplicationParameter
                  class="mt-8 mb-8"
                  ref="applicationParameterRef"
                  v-if="showTast === 'agent' + index && applicationDetailsDict[item.source_id]"
                  :application="applicationDetailsDict[item.source_id]"
                  :trigger="form"
                  v-model="item.parameter"
                ></ApplicationParameter>
              </div>
            </template>
          </div>
          <!-- 资源端工具 -->
          <div class="w-full" v-if="resourceType === 'TOOL'">
            <template v-for="(item, index) in toolTask" :key="index">
              <div class="border border-r-6 white-bg mb-4" style="padding: 2px 8px 5px">
                <div class="flex-between">
                  <div class="flex align-center" style="line-height: 20px">
                    <el-avatar
                      v-if="toolDetailsDict[item.source_id]?.icon"
                      shape="square"
                      :size="20"
                      style="background: none"
                      class="mr-8"
                    >
                      <img :src="resetUrl(toolDetailsDict[item.source_id]?.icon)" alt="" />
                    </el-avatar>
                    <ToolIcon v-else class="mr-8" :size="20" />

                    <div class="ellipsis-1" :title="toolDetailsDict[item.source_id]?.name">
                      {{ toolDetailsDict[item.source_id]?.name }}
                    </div>
                  </div>
                  <div style="margin-top: -2px">
                    <span class="mr-4">
                      <el-button
                        text
                        @click="showTast = showTast === 'tool' + index ? '' : 'tool' + index"
                      >
                        <el-icon
                          class="arrow-icon"
                          :class="showTast === 'tool' + index ? 'rotate-180' : ''"
                        >
                          <ArrowDown />
                        </el-icon>
                      </el-button>
                    </span>
                  </div>
                </div>
              </div>
              <ToolParameter
                class="mt-8 mb-8"
                ref="toolParameterRef"
                v-if="showTast === 'tool' + index && toolDetailsDict[item.source_id]"
                :tool="toolDetailsDict[item.source_id]"
                :trigger="form"
                v-model="item.parameter"
              ></ToolParameter>
            </template>
          </div>
        </template>
        <!-- 触发器 -->
        <el-card
          shadow="never"
          class="card-never w-full"
          style="--el-card-padding: 8px 12px"
          v-else
        >
          <!-- 智能体    -->
          <div class="flex-between" @click="collapseData.agent = !collapseData.agent">
            <div class="flex align-center lighter cursor">
              <el-icon class="mr-8 arrow-icon" :class="collapseData.agent ? 'rotate-90' : ''">
                <CaretRight />
              </el-icon>
              {{ $t('views.application.title') }}
              <span class="ml-4" v-if="applicationTask?.length">
                ({{ applicationTask?.length }})</span
              >
            </div>
            <div class="flex">
              <el-button type="primary" link @click.stop="openApplicationDialog()">
                <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
              </el-button>
            </div>
          </div>
          <div class="w-full" v-if="collapseData.agent">
            <template v-for="(item, index) in applicationTask" :key="index">
              <div class="border border-r-6 white-bg" style="padding: 2px 8px">
                <div class="flex-between">
                  <div class="flex align-center" style="line-height: 20px">
                    <el-avatar
                      v-if="applicationDetailsDict[item.source_id]?.icon"
                      shape="square"
                      :size="20"
                      style="background: none"
                      class="mr-8"
                    >
                      <img :src="resetUrl(applicationDetailsDict[item.source_id]?.icon)" alt="" />
                    </el-avatar>
                    <AppIcon v-else class="mr-8" :size="20" />

                    <div class="ellipsis-1" :title="applicationDetailsDict[item.source_id]?.name">
                      {{ applicationDetailsDict[item.source_id]?.name }}
                    </div>
                  </div>
                  <div style="margin-top: -2px">
                    <span class="mr-4">
                      <el-button
                        text
                        @click="showTast = showTast === 'agent' + index ? '' : 'agent' + index"
                      >
                        <el-icon
                          class="arrow-icon"
                          :class="showTast === 'agent' + index ? 'rotate-180' : ''"
                        >
                          <ArrowDown />
                        </el-icon>
                      </el-button>
                    </span>
                    <span class="mr-4">
                      <el-button text @click="deleteTask(item)">
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </span>
                  </div>
                </div>
                <ApplicationParameter
                  class="mt-8 mb-8"
                  ref="applicationParameterRef"
                  v-if="showTast === 'agent' + index && applicationDetailsDict[item.source_id]"
                  :application="applicationDetailsDict[item.source_id]"
                  :trigger="form"
                  v-model="item.parameter"
                ></ApplicationParameter>
              </div>
            </template>
          </div>
          <!-- 工具    -->
          <div class="flex-between" @click="collapseData.tool = !collapseData.tool">
            <div class="flex align-center lighter cursor">
              <el-icon class="mr-8 arrow-icon" :class="collapseData.tool ? 'rotate-90' : ''">
                <CaretRight />
              </el-icon>
              {{ $t('views.tool.title') }}
              <span class="ml-4" v-if="toolTask?.length"> ({{ toolTask?.length }})</span>
            </div>
            <div class="flex">
              <el-button type="primary" link @click.stop="openToolDialog()">
                <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
              </el-button>
            </div>
          </div>
          <div class="w-full" v-if="collapseData.tool">
            <template v-for="(item, index) in toolTask" :key="index">
              <div class="border border-r-6 white-bg mb-4" style="padding: 2px 8px 5px">
                <div class="flex-between">
                  <div class="flex align-center" style="line-height: 20px">
                    <el-avatar
                      v-if="toolDetailsDict[item.source_id]?.icon"
                      shape="square"
                      :size="20"
                      style="background: none"
                      class="mr-8"
                    >
                      <img :src="resetUrl(toolDetailsDict[item.source_id]?.icon)" alt="" />
                    </el-avatar>
                    <ToolIcon v-else class="mr-8" :size="20" />

                    <div class="ellipsis-1" :title="toolDetailsDict[item.source_id]?.name">
                      {{ toolDetailsDict[item.source_id]?.name }}
                    </div>
                  </div>
                  <div style="margin-top: -2px">
                    <span class="mr-4">
                      <el-button
                        text
                        @click="showTast = showTast === 'tool' + index ? '' : 'tool' + index"
                      >
                        <el-icon
                          class="arrow-icon"
                          :class="showTast === 'tool' + index ? 'rotate-180' : ''"
                        >
                          <ArrowDown />
                        </el-icon>
                      </el-button>
                    </span>
                    <span class="mr-4">
                      <el-button text @click="deleteTask(item)">
                        <el-icon><Close /></el-icon>
                      </el-button>
                    </span>
                  </div>
                </div>
              </div>
              <ToolParameter
                class="mt-8 mb-8"
                ref="toolParameterRef"
                v-if="showTast === 'tool' + index && toolDetailsDict[item.source_id]"
                :tool="toolDetailsDict[item.source_id]"
                :trigger="form"
                v-model="item.parameter"
              ></ToolParameter>
            </template>
          </div>
        </el-card>
      </el-form-item>
    </el-form>
    <ApplicationDialog @refresh="applicationRefresh" ref="applicationDialogRef"></ApplicationDialog>
    <ToolDialog @refresh="toolRefresh" ref="toolDialogRef"></ToolDialog>
    <template #footer>
      <el-button @click="close">{{ $t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submit">{{
        is_edit ? $t('common.save') : $t('common.create')
      }}</el-button>
    </template>
  </el-drawer>
</template>
<script setup lang="ts">
import { v4 as uuidv4 } from 'uuid'
import { ref, computed, onMounted, reactive } from 'vue'
import { copyClick } from '@/utils/clipboard'
import ApplicationDialog from '@/views/application/component/ApplicationDialog.vue'
import ToolDialog from '@/views/application/component/ToolDialog.vue'
import applicationAPI from '@/api/application/application'
import triggerAPI from '@/api/trigger/trigger'
import toolAPI from '@/api/tool/tool'
import ToolParameter from './ToolParameter.vue'
import ApplicationParameter from './ApplicationParameter.vue'
import { resetUrl } from '@/utils/common.ts'
import { t } from '@/locales'
import { type FormInstance } from 'element-plus'
import Result from '@/request/Result'

const emit = defineEmits(['refresh'])
const props = withDefaults(
  defineProps<{
    createTrigger?: (trigger: any) => Promise<Result<any>>
    editTrigger?: (trigger_id: string, trigger: any) => Promise<Result<any>>
    resourceType?: string
  }>(),
  {
    createTrigger: triggerAPI.postTrigger,
    editTrigger: triggerAPI.putTrigger,
    resourceType: '',
  },
)

const collapseData = reactive({
  tool: true,
  agent: true,
})
const showTast = ref<string>('')

const triggerFormRef = ref<FormInstance>()
const copy = () => {
  copyClick(event_url.value)
}
const addParameter = () => {
  form.value.trigger_setting.body.push({ field: '', type: '' })
}
const delParameter = (index: number | string) => {
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
const deleteTask = (task: any) => {
  form.value.trigger_task = form.value.trigger_task.filter(
    (t: any) => !(t.source_type === task.source_type && t.source_id === task.source_id),
  )
}
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
  const time = i.toString().padStart(2, '0') + ':00'
  return { label: time, value: time }
})
const days = Array.from({ length: 31 }, (_, i) => {
  i = i + 1
  const day = i.toString() + t('views.trigger.triggerCycle.days')
  return { label: day, value: i.toString(), children: times }
})
const hours = Array.from({ length: 24 }, (_, i) => {
  i = i + 1
  const time = i.toString().padStart(2, '0')
  return { label: time, value: i }
})
const minutes = Array.from({ length: 60 }, (_, i) => {
  i = i + 1
  const time = i.toString().padStart(2, '0')
  return { label: time, value: i }
})

const options = [
  {
    value: 'daily',
    label: t('views.trigger.triggerCycle.daily'),
    multiple: true,
    children: times,
  },
  {
    value: 'weekly',
    label: t('views.trigger.triggerCycle.weekly'),
    children: [
      { label: t('views.trigger.triggerCycle.sunday'), value: 7, children: times },
      { label: t('views.trigger.triggerCycle.monday'), value: 1, children: times },
      { label: t('views.trigger.triggerCycle.tuesday'), value: 2, children: times },
      { label: t('views.trigger.triggerCycle.wednesday'), value: 3, children: times },
      { label: t('views.trigger.triggerCycle.thursday'), value: 4, children: times },
      { label: t('views.trigger.triggerCycle.friday'), value: 5, children: times },
      { label: t('views.trigger.triggerCycle.saturday'), value: 6, children: times },
    ],
  },
  { value: 'monthly', label: t('views.trigger.triggerCycle.monthly'), children: days },
  {
    value: 'interval',
    label: t('views.trigger.triggerCycle.interval'),
    children: [
      { label: t('views.trigger.triggerCycle.hours'), value: 'hours', children: hours },
      { label: t('views.trigger.triggerCycle.minutes'), value: 'minutes', children: minutes },
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
        return [schedule_type, interval_unit, interval_value].filter((item) => item !== undefined)
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
      form.value.trigger_setting.interval_unit = value[1]
      form.value.trigger_setting.interval_value = value[2]
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
const current_trigger_id = ref<string>()
const open = (trigger_id?: string, source_type?: string, source_id?: string) => {
  is_edit.value = trigger_id ? true : false
  current_trigger_id.value = trigger_id
  drawer.value = true
  if (trigger_id) {
    init(trigger_id)
  }
  if (source_type && source_id) {
    if (source_type == 'APPLICATION') {
      applicationRefresh({ application_ids: [source_id] })
    }
    if (source_type == 'TOOL') {
      toolRefresh({ tool_ids: [source_id] })
    }
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
    if (is_edit.value) {
      if (current_trigger_id.value) {
        props.editTrigger(current_trigger_id.value, form.value).then((ok) => {
          close()
          emit('refresh')
        })
      }
    } else {
      props.createTrigger(form.value).then((ok) => {
        close()
        emit('refresh')
      })
    }
  })
}
onMounted(() => {})
defineExpose({ open, close })
</script>
<style lang="scss" scoped></style>
