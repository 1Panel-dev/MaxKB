<template>
  <el-row> </el-row>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import _ from 'lodash'

const props = defineProps<{
  formValue?: any
  formfieldList?: Array<FormField>
  field: string
  otherParams: any
  formField: FormField
  view?: boolean
}>()
</script>
<style lang="scss" scoped></style>
