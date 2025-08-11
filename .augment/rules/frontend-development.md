# MaxKB Frontend Development Rules

## Vue.js 3 Development Standards

### Component Structure
- Use Vue 3 Composition API for all new components
- Follow single-file component (SFC) structure
- Use `<script setup>` syntax for cleaner code
- Implement proper TypeScript typing
- Example structure:
```vue
<template>
  <div class="component-name">
    <!-- Template content -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { ComponentProps } from './types'

// Component logic
</script>

<style scoped lang="scss">
.component-name {
  // Styles
}
</style>
```

### TypeScript Integration
- Use TypeScript for all new frontend code
- Define proper interfaces for props and emits
- Use generic types for reusable components
- Implement proper type guards for API responses
- Example:
```typescript
interface ChatProfile {
  id: string
  name: string
  avatar?: string
  status: 'online' | 'offline' | 'busy'
  created_time: string
}

const props = defineProps<{
  profile: ChatProfile
  editable?: boolean
}>()

const emit = defineEmits<{
  update: [profile: ChatProfile]
  delete: [id: string]
}>()
```

## Element Plus UI Framework

### Component Usage
- Use Element Plus components consistently
- Follow Element Plus design guidelines
- Customize themes using CSS variables
- Implement proper form validation with Element Plus
- Use Element Plus icons and typography

### Form Handling
- Use `el-form` with proper validation rules
- Implement reactive form validation
- Handle form submission with loading states
- Example:
```vue
<el-form :model="form" :rules="rules" ref="formRef">
  <el-form-item label="Name" prop="name">
    <el-input v-model="form.name" />
  </el-form-item>
</el-form>
```

### Table and Data Display
- Use `el-table` for data tables
- Implement proper pagination with `el-pagination`
- Add sorting and filtering capabilities
- Handle loading and empty states

## State Management with Pinia

### Store Structure
- Create feature-based stores
- Use composition API style stores
- Implement proper TypeScript typing
- Handle async operations properly
- Example:
```typescript
export const useChatStore = defineStore('chat', () => {
  const chatList = ref<ChatProfile[]>([])
  const loading = ref(false)
  
  const fetchChatList = async () => {
    loading.value = true
    try {
      const response = await chatApi.getList()
      chatList.value = response.data
    } finally {
      loading.value = false
    }
  }
  
  return {
    chatList,
    loading,
    fetchChatList
  }
})
```

## API Integration

### HTTP Client Setup
- Use Axios for HTTP requests
- Implement request/response interceptors
- Handle authentication tokens automatically
- Implement proper error handling
- Example:
```typescript
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### API Service Pattern
- Create service modules for different API endpoints
- Use TypeScript interfaces for request/response types
- Implement proper error handling
- Support loading states
- Example:
```typescript
export const chatApi = {
  async getProfile(chatId: string): Promise<ApiResponse<ChatProfile>> {
    const response = await api.get(`/chat/${chatId}/profile`)
    return response.data
  },
  
  async updateProfile(chatId: string, data: Partial<ChatProfile>): Promise<ApiResponse<ChatProfile>> {
    const response = await api.put(`/chat/${chatId}/profile`, data)
    return response.data
  }
}
```

## TypeScript Type Definitions

### Interface Naming Conventions
- Use PascalCase for interface names
- Add descriptive suffixes (Profile, Config, Response, etc.)
- Group related interfaces in type files
- Export interfaces for reuse across components

### API Response Types
- Define consistent response wrapper types
- Use generic types for different data structures
- Handle optional and nullable fields properly
- Example:
```typescript
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

interface PageResponse<T> extends ApiResponse<T[]> {
  total: number
  current_page: number
  page_size: number
}

interface ChatMessage {
  id: string
  content: string
  sender_id: string
  chat_id: string
  created_time: string
  message_type: 'text' | 'image' | 'file'
}
```

## Component Development

### Reusable Components
- Create generic, reusable components
- Use props and slots for customization
- Implement proper prop validation
- Document component APIs
- Example:
```vue
<script setup lang="ts">
interface Props {
  title: string
  loading?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  size: 'medium'
})
</script>
```

### Event Handling
- Use proper event naming conventions
- Implement event payload typing
- Handle async events properly
- Use event modifiers when appropriate

## Styling and CSS

### SCSS Usage
- Use SCSS for styling
- Implement CSS variables for theming
- Follow BEM naming convention
- Use scoped styles in components
- Example:
```scss
.chat-profile {
  &__avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  
  &__name {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  
  &--online {
    .chat-profile__status {
      color: var(--el-color-success);
    }
  }
}
```

### Responsive Design
- Use CSS Grid and Flexbox for layouts
- Implement mobile-first responsive design
- Use Element Plus breakpoint utilities
- Test on different screen sizes

## Performance Optimization

### Code Splitting
- Use dynamic imports for route components
- Implement component lazy loading
- Split vendor bundles appropriately
- Use Vite's built-in optimizations

### Reactivity Optimization
- Use `shallowRef` for large objects when appropriate
- Implement proper `v-memo` usage
- Use `markRaw` for non-reactive data
- Optimize computed properties

## Error Handling

### Global Error Handling
- Implement global error handlers
- Show user-friendly error messages
- Log errors for debugging
- Handle network errors gracefully

### Component Error Boundaries
- Use error boundaries for component isolation
- Implement fallback UI for errors
- Provide error recovery mechanisms
- Log component errors properly

## Chat-Specific Development Patterns

### Real-time Communication
- Use WebSocket for real-time chat features
- Implement proper connection management
- Handle reconnection scenarios
- Manage message queuing during disconnections

### Message Rendering
- Support multiple message types (text, image, file)
- Implement proper message formatting
- Handle markdown and code highlighting
- Support message reactions and threading

### Chat UI Components
- Create reusable chat bubble components
- Implement proper scrolling behavior
- Handle message loading and pagination
- Support typing indicators and read receipts
