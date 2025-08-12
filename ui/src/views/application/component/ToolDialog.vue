<template>
  <el-dialog
    align-center
    :title="$t('common.setting')"
    v-model="dialogVisible"
    style="width: 550px"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      label-position="top"
      ref="paramFormRef"
      :model="form"
      require-asterisk-position="right"
    >
      <el-form-item>
        <el-select v-model="form.tool_ids" filterable multiple>
          <el-option
            v-for="mcpTool in toolSelectOptions"
            :key="mcpTool.id"
            :label="mcpTool.name"
            :value="mcpTool.id"
          >
            <span>{{ mcpTool.name }}</span>
            <el-tag v-if="mcpTool.scope === 'SHARED'" type="info" class="info-tag ml-8 mt-4">
              {{ $t('views.shared.title') }}
            </el-tag>
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submit()" :loading="loading">
          {{ $t('common.save') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import {ref, watch} from 'vue'

const emit = defineEmits(['refresh'])

const paramFormRef = ref()

const form = ref<any>({
  tool_ids: [],
})

const toolSelectOptions = ref<any[]>([])

const dialogVisible = ref<boolean>(false)

const loading = ref(false)

watch(dialogVisible, (bool) => {
  if (!bool) {
    form.value = {
      tool_ids: [],
    }
  }
})


const open = (data: any, selectOptions: any) => {
  form.value = {...form.value, ...data}
  dialogVisible.value = true
  toolSelectOptions.value = selectOptions
}

const submit = () => {
  paramFormRef.value.validate().then((valid: any) => {
    if (valid) {
      emit('refresh', form.value)
      dialogVisible.value = false
    }
  })
}



defineExpose({open})
</script>
<style lang="scss" scoped></style>
