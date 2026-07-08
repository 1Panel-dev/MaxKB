import type { App } from 'vue'
export default {
  install: (app: App) => {
    app.directive('resize', {
      created(el: any, binding: any) {
        // 记录长宽
        let width = ''
        let height = ''
        function getSize() {
          const style = (document.defaultView as any).getComputedStyle(el)
          // 如果当前长宽和历史长宽不同
          if (width !== style.width || height !== style.height) {
            // binding.value在这里就是下面的resizeChart函数

            binding.value({
              width: parseFloat(style.width),
              height: parseFloat(style.height)
            })
          }
          width = style.width
          height = style.height
        }

        ;(el as any).__vueDomResize__ = setInterval(getSize, 500)
      },
      unmounted(el: any, binding: any) {
        clearInterval((el as any).__vueDomResize__)
      }
    })
  }
}
