import { ref, onMounted } from "vue";

const isDark = ref(false);

export function useTheme() {
  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
      isDark.value = true;
      document.documentElement.classList.add("dark");
    } else if (saved === "light") {
      isDark.value = false;
      document.documentElement.classList.remove("dark");
    } else {
      // Check system preference
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      isDark.value = prefersDark;
      if (prefersDark) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }

  function toggleTheme() {
    isDark.value = !isDark.value;
    if (isDark.value) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }

  return {
    isDark,
    initTheme,
    toggleTheme
  };
}
