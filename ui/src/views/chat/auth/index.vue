<template>
  <component
    :is="auth_components[`/src/views/chat/auth/component/${auth_type}.vue`].default"
    v-model="is_auth"
    :applicationProfile="application_profile"
  />
</template>
<script setup lang="ts">
import { computed } from 'vue'

const auth_components: any = import.meta.glob('@/views/chat/auth/component/*.vue', {
  eager: true,
})

const emit = defineEmits(['update:modelValue'])

const props = withDefaults(
  defineProps<{ modelValue: boolean; application_profile: any; auth_type?: string; style?: any }>(),
  {
    auth_type: 'password',
    style: {},
  },
)
const is_auth = computed({
  get: () => {
    return props.modelValue
  },
  set: (v) => {
    emit('update:modelValue', v)
  },
})
</script>
<style lang="scss"></style>
