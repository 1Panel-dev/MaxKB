import type { Component } from 'vue'

const icons = import.meta.glob<{ default: Component }>('./**.vue', { eager: true })
export function iconComponent(name: string) {
  const url = `./${name}.vue`
  return icons[url]?.default || null
}
