<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '@/stores/admin'
import { LOCALE_OPTIONS } from '@/locales/config'
import { useRouter } from 'vue-router'

const router = useRouter()
const { t } = useI18n({ useScope: 'global' })
const { user } = useStore()
const language = computed({ get: () => user.language, set: (value: string) => user.setLanguage(value) })

function goHome() {
  void router.replace({ name: 'workspace-home', params: { workspaceId: 'default' } })
}
</script>

<template>
  <main class="flex-center min-h-screen">
    <el-result icon="warning" title="404" :sub-title="t('common.errors.notFound.description')">
      <template #extra>
        <!-- 返回工作空间首页 -->
        <el-button type="primary" @click="goHome">{{ t('common.actions.goHome') }}</el-button>
        <!-- 切换界面语言 -->
        <div class="mt-16">
          <label for="error-page-language">{{ t('common.fields.language.label') }}</label>
          <el-select id="error-page-language" v-model="language" class="ml-8" style="width: 140px">
            <template v-for="option in LOCALE_OPTIONS" :key="option.value">
              <el-option :label="option.label" :value="option.value" />
            </template>
          </el-select>
        </div>
      </template>
    </el-result>
  </main>
</template>
