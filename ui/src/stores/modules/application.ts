import { defineStore } from 'pinia'
import { type Ref } from 'vue'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${window.location.origin}${window.MaxKB.chatPrefix ? window.MaxKB.chatPrefix : window.MaxKB.prefix}/`,
  }),
  actions: {},
})

export default useApplicationStore
