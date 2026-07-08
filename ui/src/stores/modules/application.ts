import { defineStore } from 'pinia'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${getChatOrigin()}${
      window.MaxKB.chatPrefix ? window.MaxKB.chatPrefix : window.MaxKB.prefix
    }/`,
  }),
  actions: {},
})

function getChatOrigin() {
  if (import.meta.env.DEV && window.location.port === '3000') {
    return `${window.location.protocol}//${window.location.hostname}:3001`
  }
  return window.location.origin
}

export default useApplicationStore
