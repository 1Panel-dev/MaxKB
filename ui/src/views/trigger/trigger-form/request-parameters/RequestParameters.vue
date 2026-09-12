<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { TRIGGER_BODY_TYPE } from '@/api/enums'
import type { TriggerBodyField } from '@/api/types'
import RequestParameterDialog from './RequestParameterDialog.vue'

const body = defineModel<TriggerBodyField[] | undefined>({ required: true })
const fields = computed({
  get: () => body.value ?? [],
  set: (value: TriggerBodyField[]) => {
    body.value = value
  },
})
const dialogRef = useTemplateRef<InstanceType<typeof RequestParameterDialog>>('dialogRef')
const defaultField: TriggerBodyField = { field: '', type: TRIGGER_BODY_TYPE.STRING, desc: '', required: false }

function saveField(field: TriggerBodyField, index?: number) {
  const updatedFields = cloneDeep(fields.value)
  if (index === undefined) updatedFields.push(cloneDeep(field))
  else updatedFields.splice(index, 1, cloneDeep(field))
  fields.value = updatedFields
  dialogRef.value?.close()
}
</script>

<template>
  <div class="w-full">
    <div class="flex-between mt-4 mb-2">
      <h6>请求参数</h6>
      <!-- 添加请求参数 -->
      <el-button text type="primary" @click="dialogRef?.open()">
        <MkIcon name="icon_add_outlined" />
      </el-button>
    </div>
    <MkFormList v-model="fields" :default-item="defaultField" :min-rows="0" :first-row-has-label="false" :show-add-button="false">
      <template #default="{ item, index }">
        <div class="mb-4 flex min-w-0 flex-1 items-start gap-2">
          <div class="min-w-0 flex-1 pt-1">
            <div class="flex items-center gap-2">
              <span class="truncate" :title="item.field">{{ item.field }}</span>
              <el-tag size="small" type="info">{{ item.type }}</el-tag>
              <span v-if="item.required" class="shrink-0 text-danger">*</span>
            </div>
            <p v-if="item.desc" class="truncate text-sm text-N600" :title="item.desc">{{ item.desc }}</p>
          </div>
          <!-- 编辑请求参数 -->
          <el-button text class="mt-1" @click="dialogRef?.open(item, index)">
            <MkIcon name="icon_edit_outlined" class="text-N600" />
          </el-button>
        </div>
      </template>
    </MkFormList>
    <RequestParameterDialog ref="dialogRef" :fields="fields" @submit="saveField" />
  </div>
</template>
