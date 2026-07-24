# MaxKB v3 Frontend

This document is for frontend agents working in the `ui/` project.

## Documentation Workflow

`AGENTS.md` is the Codex-maintained entry point for project-wide instructions. It provides the project overview, shared conventions, and an index of topic-specific rule documents; it does not replace the detailed rules owned by those documents.

Before making changes, determine which areas the task touches and read the corresponding rule documents:

- Styles: `src/styles/STYLE_README.md` is the source of truth for styling rules.
- Router: `src/router/ROUTE_README.md` is the source of truth for routing rules.
- Components: `src/components/COMPONENT_README.md` is the source of truth for component rules.
- Constants: `src/constants/CONSTANT_README.md` is the source of truth for shared constant rules.
- Utilities: `src/utils/UTILS_README.md` is the source of truth for shared utility rules.

Follow this maintenance flow:

1. Use `AGENTS.md` to understand the project-wide context and locate applicable rule documents.
2. Read every applicable rule document before implementing or reviewing changes in that area.
3. Keep detailed, area-specific guidance in its owning README; keep only the summary and document index in `AGENTS.md`.
4. When a new area-specific rule README is added, append it to the list above and reference it in the relevant project-structure or responsibility section of `AGENTS.md`.
5. When a rule changes, update its owning README and adjust the summary in `AGENTS.md` only when the project-wide guidance or index also changes.

## Stack

- Vue 3.5 with `<script setup lang="ts">`
- TypeScript 6
- Vite 8
- Vue Router 5
- Pinia 3
- Tailwind CSS 4 through `@tailwindcss/vite`
- Sass through Vite's native Sass support
- Element Plus

## Project Structure

```text
ui/
├── admin.html                 # Admin application HTML entry
├── chat.html                  # Chat application HTML entry
├── env/                       # Environment variables for each application mode
├── public/                    # Static files copied to the build output as-is
├── src/
│   ├── App.vue               # Root Vue component and router outlet
│   ├── main.ts               # Admin application bootstrap
│   ├── chat.ts               # Chat application bootstrap
│   ├── assets/                # Images and other source-controlled visual assets
│   │   ├── iconfont.js        # Generated SVG Symbol resource; replace, do not edit
│   │   ├── logo/             # Product and brand logos
│   │   └── workflow/         # Workflow-related visual assets
│   ├── components/            # Shared UI components
│   │   ├── COMPONENT_README.md # Shared component conventions and usage
│   │   ├── global/            # Frequently used components auto-registered by Vite
│   │   │   └── mk-icon/       # Unified SVG Symbol and Element Plus icon component
│   │   └── <component-name>/   # Less-frequent shared components imported explicitly
│   ├── constants/             # Cross-feature constants grouped by domain
│   │   └── CONSTANT_README.md # Shared constant placement and naming rules
│   ├── layout/                # Shared application shells, headers, sidebars, and layout types
│   ├── locales/               # Reserved for internationalization messages and locale setup
│   ├── router/                # Vue Router routes and router instance
│   │   └── ROUTE_README.md    # Routing conventions and rules
│   ├── stores/                # Shared Pinia state stores
│   ├── styles/                # Global styles, theme tokens, and third-party style integration
│   │   ├── font/             # Locally hosted application fonts
│   │   ├── variables.scss    # Canonical runtime `--mk-*` color and theme variables
│   │   ├── element-plus.scss # Element Plus Sass configuration and CSS-variable mapping
│   │   ├── tailwind.css      # Tailwind import and `mk-*` theme token mapping
│   │   ├── app.scss          # Fonts, base element styles, and app-wide defaults
│   │   ├── index.scss        # Sass entry that aggregates global Sass modules
│   │   └── STYLE_README.md    # Local UI conventions and color-variable usage examples
│   ├── utils/                 # Cross-feature utilities grouped by domain or capability
│   │   └── UTILS_README.md    # Shared utility placement and naming rules
│   ├── views/                 # Route-level page components grouped by feature
│   │   ├── home/             # Workspace home page
│   │   ├── system/           # System-management pages
│   │   ├── login/            # Reserved for admin login pages
│   │   └── chat/             # Chat-side pages, including user login
│   └── workflow/              # Workflow editor domain code
│       └── nodes/             # Workflow node definitions and components
├── vite.config.ts            # Vite entries, plugins, aliases, proxy, and build output
├── tsconfig*.json            # TypeScript configuration
└── package.json              # Dependencies and npm scripts
```

Directories marked as reserved may be empty while their feature is being introduced. Add files to the matching feature directory instead of creating parallel top-level structures.

Structural responsibilities:

- Put reusable application chrome in `layout/`, not in individual route views.
- Put constants shared by most pages or multiple business modules in `constants/`, and split files by a specific domain. Keep constants used by only one page or feature with their owning code.
- Put route-level screens in `views/<feature>/`; keep reusable feature components below their owning feature when they are not globally shared.
- Put shared client state in `stores/`; component-local state should remain in the component.
- Put functions shared by most pages or multiple business modules in `utils/`; detailed placement, file organization, and naming rules are maintained in `src/utils/UTILS_README.md`.
- Import source assets through `src/assets/`; use `public/` only when a file must retain its original filename and URL.

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

## Frontend Implementation Notes

- Prefer existing project structure and naming.
- Keep UI code typed and data-driven.
- Name business variables after their domain and purpose. Avoid context-free collection names such as
  `items` or `list` when a name such as `systemMenuItems` makes the contents clear.
