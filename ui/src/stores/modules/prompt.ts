import { defineStore } from 'pinia'

export interface promptTypes {
  user: string
  formValue: { model_id: string, prompt: string }
}

const usePromptStore = defineStore({
  id: 'prompt',
  state: (): promptTypes[] => (JSON.parse(localStorage.getItem('PROMPT_CACHE') || '[]')),
  actions: {
    save(user: string, formValue: any) {
      this.$state.forEach((item: any, index: number) => {
        if (item.user === user) {
          this.$state.splice(index, 1)
        }
      })
      this.$state.push({ user, formValue })
      localStorage.setItem('PROMPT_CACHE', JSON.stringify(this.$state))
    },
    get(user: string) {
      for (let i = 0; i < this.$state.length; i++) {
        if (this.$state[i].user === user) {
          return this.$state[i].formValue
        }
      }
      return {
        model_id: '',
        prompt: '内容：{data}\n' +
          '\n' +
          '请总结上面的内容，并根据内容总结生成 5 个问题。\n' +
          '回答要求：\n' +
          '- 请只输出问题；\n' +
          '- 请将每个问题放置<question></question>标签中。'
      }
    }
  }
})

export default usePromptStore