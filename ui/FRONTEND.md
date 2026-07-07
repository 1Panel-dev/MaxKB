# MaxKB v3 Frontend

This document is for frontend agents working in the `ui/` project.

## Stack

- Vue 3.5 with `<script setup lang="ts">`
- TypeScript 6
- Vite 8
- Vue Router 5
- Pinia 3
- Tailwind CSS 4 through `@tailwindcss/vite`
- Sass through Vite's native Sass support
- Element Plus with automatic component/import registration

Do not add `sass-loader`; this is a Vite project, not a Webpack project.

## Entry Points

The frontend is designed as a multi-entry app:

- Admin entry: `admin.html` -> `src/main.ts`
- Chat entry: `chat.html` -> `src/chat.ts`

Environment files live in `env/`:

- `env/.env` for admin
- `env/.env.chat` for chat

Important variables:

- `VITE_APP_NAME`: app name, such as `admin` or `chat`
- `VITE_BASE_PATH`: deployed base path, such as `/admin/` or `/chat/`
- `VITE_APP_PORT`: local dev server port
- `VITE_APP_TITLE`: HTML title
- `VITE_ENTRY`: HTML entry file
- `VITE_API_TARGET`: optional backend proxy target, defaults to `http://127.0.0.1:8080`

Build output mirrors the v2 layout:

- Admin builds to `dist/admin/index.html`
- Chat builds to `dist/chat/index.html`

The Vite config builds `admin.html` or `chat.html` first, then renames the entry HTML to `index.html` inside the relevant output directory.

## Commands

Run commands from `ui/`.

```bash
npm install
npm run dev          # admin dev server
npm run chat         # chat dev server
npm run build        # default admin build with type-check
npm run build-chat   # chat build with type-check
npm run type-check
npm run lint
npm run format
```

## Vite Configuration

Main config: `vite.config.ts`.

Keep these behaviors:

- `base: './'` for v2-compatible static deployment.
- `envDir: './env'`.
- Proxy `/admin/api`, `/chat/api`, `/doc`, `/schema`, `/static`, and `oss` file paths to the backend.
- Keep Tailwind, Vue, Vue JSX, Vue DevTools, Element Plus auto import, and component auto registration plugins.
- Do not add `unplugin-vue-define-options`; Vue 3.5 already supports `defineOptions`.
- Avoid adding `vite-plugin-html` unless multi-template requirements exceed Vite's built-in HTML env replacement.

## Styles

Style entry imports are in both `src/main.ts` and `src/chat.ts`:

```ts
import './styles/tailwind.css'
import './styles/index.scss'
```

Style responsibilities:

- `styles/tailwind.css`: Tailwind import and Tailwind theme tokens.
- `styles/index.scss`: Sass aggregator only.
- `styles/element-plus.scss`: Element Plus Sass variable overrides and Element Plus theme import.
- `styles/app.scss`: app-wide base styles and fonts.

Keep Tailwind separate from Sass. Do not import Tailwind from `index.scss`; doing so can route Tailwind through Sass and cause build warnings or incorrect processing.

Avoid broad reset rules such as:

```scss
* {
  margin: 0;
  padding: 0;
}
```

They can break Element Plus component spacing. Prefer focused base styles such as `box-sizing`, `body { margin: 0; }`, and app-level layout rules.

## Element Plus

Element Plus is auto-registered through:

- `unplugin-auto-import`
- `unplugin-vue-components`
- `ElementPlusResolver`

Use Element Plus components directly in Vue templates when appropriate:

```vue
<el-button type="primary">保存</el-button>
```

Generated declarations:

- `src/auto-imports.d.ts`
- `src/components.d.ts`

Keep `ElementPlusResolver({ importStyle: false })` because styles are loaded through `styles/element-plus.scss`.

## Frontend Implementation Notes

- Prefer existing project structure and naming.
- Keep UI code typed and data-driven.
- Use Tailwind utility classes for layout and small styling.
- Use Sass for shared theme, Element Plus overrides, fonts, and app-wide base rules.
- Keep component styles scoped unless they are intentionally global.
- Do not introduce new UI libraries unless there is a concrete need.
- After config or style changes, run:

```bash
npm run type-check
npm run build-only
npm run build-only:chat
```
