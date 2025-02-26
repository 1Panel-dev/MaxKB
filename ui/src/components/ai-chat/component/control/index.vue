<template>
  <div>
    <vue3-menus v-model:open="isOpen" :event="eventVal" :zIndex="9999" :menus="menus" hasIcon>
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
const eventVal = ref<any>({})

function getSelection() {
  const selection = window.getSelection()
  if (selection) {
    if (selection.rangeCount === 0) return undefined
    const range = selection.getRangeAt(0)
    const fragment = range.cloneContents() // 克隆选区内容
    const div = document.createElement('div')
    div.appendChild(fragment)
    if (div.textContent) {
      return div.textContent.trim()
    }
  }
  return undefined
}

/**
 * 打开控制台
 * @param event
 */
const openControl = (event: any) => {
  const c = getSelection()
  if (c) {
    if (!isOpen.value) {
      nextTick(() => {
        eventVal.value = event
        isOpen.value = true
      })
    } else {
      clearSelectedText()
      isOpen.value = false
    }
    event.preventDefault()
  } else {
    isOpen.value = false
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
        if (
          typeof navigator.clipboard === 'undefined' ||
          typeof navigator.clipboard.writeText === 'undefined'
        ) {
          const input = document.createElement('input')
          input.setAttribute('value', selectionText)
          document.body.appendChild(input)
          input.select()
          try {
            if (document.execCommand('copy')) {
              MsgSuccess(t('common.copySuccess'))
            }
          } finally {
            document.body.removeChild(input)
          }
        } else {
          navigator.clipboard.writeText(selectionText).then(() => {
            MsgSuccess(t('common.copySuccess'))
          })
        }
      }
    }
  },
  {
    label: t('chat.quote'),
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
