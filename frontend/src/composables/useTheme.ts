import { ref } from 'vue'

type Theme = 'light' | 'dark'
const KEY = 'hirelens:theme'

function stored(): Theme | null {
  try {
    const v = localStorage.getItem(KEY)
    return v === 'light' || v === 'dark' ? v : null
  } catch {
    return null
  }
}

function system(): Theme {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const theme = ref<Theme>(stored() ?? system())

function apply(value: Theme, remember: boolean) {
  theme.value = value
  document.documentElement.dataset.theme = value
  if (remember) {
    try {
      localStorage.setItem(KEY, value)
    } catch {
      /* not remembered; still applied for this visit */
    }
  }
}

// Only pin the theme on <html> once the visitor has chosen; otherwise CSS follows the system.
if (stored()) apply(stored()!, false)

export function useTheme() {
  return {
    theme,
    toggle: () => apply(theme.value === 'dark' ? 'light' : 'dark', true),
  }
}
