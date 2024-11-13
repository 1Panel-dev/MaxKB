<template>
  <div class="chat-pc__header" :style="customStyle">
    <div class="flex align-center">
      <div class="mr-12 ml-24 flex">
        <AppAvatar
          v-if="isAppIcon(application_profile?.icon)"
          shape="square"
          :size="32"
          style="background: none"
        >
          <img :src="application_profile?.icon" alt="" />
        </AppAvatar>
        <AppAvatar
          v-else-if="application_profile?.name"
          :name="application_profile?.name"
          pinyinColor
          shape="square"
          :size="32"
        />
      </div>
      <h4>{{ application_profile?.name }}</h4>
    </div>
  </div>

  <component
    :is="auth_components[`/src/views/chat/auth/component/${auth_type}.vue`].default"
    v-model="is_auth"
    :applicationProfile="application_profile"
  />
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { isAppIcon } from '@/utils/application'

const auth_components: any = import.meta.glob('@/views/chat/auth/component/*.vue', {
  eager: true
})

const emit = defineEmits(['update:modelValue'])

const props = withDefaults(
  defineProps<{ modelValue: boolean; application_profile: any; auth_type?: string; style?: any }>(),
  {
    auth_type: 'password',
    style: {}
  }
)
const is_auth = computed({
  get: () => {
    return props.modelValue
  },
  set: (v) => {
    emit('update:modelValue', v)
  }
})

const customStyle = computed(() => {
  return {
    background: props.application_profile?.custom_theme?.theme_color,
    color: props.application_profile?.custom_theme?.header_font_color,
    border: 'none',
    ...props.style
  }
})
</script>
<style lang="scss"></style>
