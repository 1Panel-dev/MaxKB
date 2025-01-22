import { defineStore } from 'pinia'
import { t } from '@/locales'
export interface promptTypes {
  user: string
  formValue: { model_id: string; prompt: string }
}

const usePromptStore = defineStore({
  id: 'prompt',
  state: (): promptTypes[] => JSON.parse(localStorage.getItem('PROMPT_CACHE') || '[]'),
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
        prompt:
          t('views.document.generateQuestion.prompt1', { data: '{data}' }) +
          '<question></question>' +
          t('views.document.generateQuestion.prompt2')
      }
    }
  }
})

export default usePromptStore
