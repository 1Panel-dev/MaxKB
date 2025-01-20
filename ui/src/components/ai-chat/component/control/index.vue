<template>
  <div>
    <vue3-menus v-model:open="isOpen" :event="eventVal" :menus="menus" hasIcon>
      <template #icon="{ menu }"
        ><AppIcon v-if="menu.icon" :iconName="menu.icon"></AppIcon
      ></template>
      <template #label="{ menu }"> {{ menu.label }}</template>
    </vue3-menus>
  </div>
</template>
<script setup lang="ts">
import { Vue3Menus } from 'vue3-menus'
import { MsgSuccess } from '@/utils/message'
import AppIcon from '@/components/icons/AppIcon.vue'
import bus from '@/bus'
import { ref, nextTick, onMounted } from 'vue'
import { t } from '@/locales'
const isOpen = ref<boolean>(false)
const eventVal = ref()
function getSelection() {
  const selection = window.getSelection()
  if (selection && selection.anchorNode == null) {
    return null
  }
  const text = selection?.anchorNode?.textContent
  return text && text.substring(selection.anchorOffset, selection.focusOffset)
}
/**
 * 打开控制台
 * @param event
 */
const openControl = (event: any) => {
  const c = getSelection()
  isOpen.value = false
  if (c) {
    nextTick(() => {
      eventVal.value = event
      isOpen.value = true
    })
    event.preventDefault()
  }
}

const menus = ref([
  {
    label: t('common.copy'),
    icon: 'app-copy',
    click: () => {
      const selectionText = getSelection()
      if (selectionText) {
        clearSelectedText()
        navigator.clipboard.writeText(selectionText).then(() => {
          MsgSuccess(t('common.copySuccess'))
        })
      }
    }
  },
  {
    label: '引用',
    icon: 'app-quote',
    click: () => {
      bus.emit('chat-input', getSelection())
      clearSelectedText()
    }
  }
])
/**
 * 清除选中文本
 */
const clearSelectedText = () => {
  if (window.getSelection) {
    var selection = window.getSelection()
    if (selection) {
      selection.removeAllRanges()
    }
  }
}
onMounted(() => {
  bus.on('open-control', openControl)
})
</script>
<style lang="scss"></style>
