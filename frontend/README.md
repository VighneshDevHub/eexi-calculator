# Frontend — React + TypeScript + Vite

This directory contains the React frontend scaffold for the IMO Ship Emissions & Engineering Calculator. It is currently in early development; the production UI is served by Flask/Jinja2 templates in the parent project.

---

## Current Status

| Item | Status |
|---|---|
| Vite + React 19 + TypeScript 6 scaffold | ✅ Initialised |
| Backend API integration | 🔲 Not started |
| EEXI calculator UI | 🔲 Planned |
| CII calculator UI | 🔲 Planned |
| EGBP calculator UI | 🔲 Planned |
| Pipe Wall calculator UI | 🔲 Planned |

The active application is the Flask backend at `../app.py`. Run that with `python app.py` — no frontend build step is required for day-to-day use.

---

## Tech Stack

| Package | Version |
|---|---|
| React | 19.2 |
| TypeScript | 6.0 |
| Vite | 8.0 |
| @vitejs/plugin-react | latest |

---

## Backend API (for future integration)

The Flask backend exposes the following JSON endpoints that the React frontend will consume:

| Method | Route | Calculator |
|---|---|---|
| POST | `/api/calculate-cii` | CII — returns attained/required CII and A–E rating |
| POST | `/calculate-egbp` | EGBP — returns pressure loss breakdown and PASS/FAIL status |
| POST | `/calculate-pipe` | Pipe Wall — returns t_dis, t_min, ASME schedule recommendation |
| POST | `/api/cii-report` | CII PDF download |
| POST | `/api/egbp-report` | EGBP PDF download |
| POST | `/api/pipe-report` | Pipe Wall PDF download |

EEXI calculation uses a standard form POST to `/calculate` (Jinja2 flow — will be migrated to a JSON endpoint when this frontend is integrated).

See the root `README.md` for full request/response schemas.

---

## Development Setup

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Type check
npm run build

# Lint
npm run lint
```

The Vite dev server runs on port 5173. To proxy API calls to the Flask backend during development, add a proxy configuration to `vite.config.ts`:

```ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/calculate': 'http://127.0.0.1:5000',
    }
  }
})
```

---

## ESLint Configuration

For production, update `eslint.config.js` to enable type-aware rules:

```js
import tseslint from 'typescript-eslint'
export default tseslint.config({
  extends: [tseslint.configs.recommendedTypeChecked],
  languageOptions: {
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```
