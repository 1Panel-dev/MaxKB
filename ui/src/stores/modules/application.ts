import { defineStore } from 'pinia'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${window.location.origin}${window.MaxKB.chatPrefix ? window.MaxKB.chatPrefix : window.MaxKB.prefix}/`,
  }),
  actions: {},
})

export default useApplicationStore
