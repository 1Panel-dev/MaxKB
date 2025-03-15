<template>
  <el-drawer v-model="visible" size="40%" :append-to-body="true">
    <template #header>
      <div class="flex align-center" style="margin-left: -8px">
        <el-button class="cursor mr-4" link @click.prevent="visible = false">
          <el-icon :size="20">
            <Back />
          </el-icon>
        </el-button>
        <h4>详情</h4>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { t } from '@/locales'

const visible = ref(false)

const open = (data: any) => {
  visible.value = true
}

defineExpose({
  open
})
</script>