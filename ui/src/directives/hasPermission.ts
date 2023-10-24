import type { App } from 'vue'
import { hasPermission } from '@/utils/permission'

const display = async (el: any, binding: any) => {
  const has = hasPermission(
    binding.value?.permission || binding.value,
    binding.value?.compare || 'OR'
  )
  if (!has) {
    el.style.display = 'none'
  } else {
    delete el.style.display
  }
}

export default {
  install: (app: App) => {
    app.directive('hasPermission', {
      async created(el: any, binding: any) {
        display(el, binding)
      },
      async beforeUpdate(el: any, binding: any) {
        display(el, binding)
      }
    })
  }
}
