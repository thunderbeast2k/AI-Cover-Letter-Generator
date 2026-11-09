<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { Icon } from "@iconify/vue";
import { useTheme } from "@/composables/useTheme";
import { ApiService } from "@/services/api";
import ToastContainer from "@/components/common/ToastContainer.vue";
import Badge from "@/components/common/Badge.vue";
import type { BackendHealth } from "@/types";

const route = useRoute();
const { isDark, toggleTheme, initTheme } = useTheme();
const isMobileNavOpen = ref(false);
const health = ref<BackendHealth | null>(null);

const navItems = [
  { name: "Dashboard", path: "/", icon: "lucide:layout-dashboard" },
  { name: "Create Cover Letter", path: "/workspace", icon: "lucide:file-edit" },
  { name: "Job Analyzer", path: "/analyzer", icon: "lucide:briefcase" },
  { name: "Resume Matching", path: "/matching", icon: "lucide:git-compare" },
  { name: "My Drafts", path: "/drafts", icon: "lucide:bookmark" },
  { name: "Templates", path: "/templates", icon: "lucide:layout-template" },
  { name: "Settings", path: "/settings", icon: "lucide:settings" }
];

const checkBackend = async () => {
  try {
    health.value = await ApiService.getHealth();
  } catch (err) {
    console.warn("Backend not yet connected:", err);
  }
};

onMounted(() => {
  initTheme();
  checkBackend();
});

const isCurrentRoute = (path: string) => path === "/" ? route.path === "/" : route.path.startsWith(path);
</script>

<template>
  <div class="min-h-screen bg-background text-foreground antialiased selection:bg-primary/20">
    <ToastContainer />

    <header class="sticky top-0 z-30 px-4 pt-4 sm:px-6 lg:px-8">
      <div class="mx-auto flex h-14 max-w-7xl items-center justify-between rounded-full border border-border/70 bg-card/75 px-3 shadow-lg shadow-black/[0.03] backdrop-blur-xl sm:px-5">
        <router-link to="/" class="flex items-center gap-2.5 rounded-full pr-3">
          <span class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-slate-200 via-slate-500 to-slate-950 text-slate-950 shadow-md shadow-slate-500/25">
            <Icon icon="lucide:sparkles" class="h-4 w-4" />
          </span>
          <span class="hidden text-sm font-bold tracking-tight sm:block">CareerCraft<span class="text-primary"> AI</span></span>
        </router-link>

        <nav class="hidden items-center gap-1 lg:flex">
          <router-link
            v-for="item in navItems.slice(0, 5)"
            :key="item.path"
            :to="item.path"
            :class="[
              'rounded-full px-3 py-2 text-xs font-semibold transition-colors',
              isCurrentRoute(item.path) ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
            ]"
          >
            {{ item.name === "Create Cover Letter" ? "Create" : item.name }}
          </router-link>
        </nav>

        <div class="flex items-center gap-2 sm:gap-3">
          <Badge v-if="health?.config?.demo_mode" variant="warning" class="hidden sm:inline-flex">
            <Icon icon="lucide:test-tube" class="mr-1 h-3 w-3" />
            Demo Mode
          </Badge>
          <button
            class="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            title="Toggle Light/Dark Theme"
            @click="toggleTheme"
          >
            <Icon :icon="isDark ? 'lucide:sun' : 'lucide:moon'" class="h-4 w-4" />
          </button>
          <router-link
            to="/workspace"
            class="hidden items-center gap-1.5 rounded-full bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground shadow-sm transition-all hover:scale-[1.02] hover:bg-primary/90 sm:inline-flex"
          >
            <Icon icon="lucide:plus" class="h-3.5 w-3.5" />
            New Letter
          </router-link>
          <button
            class="rounded-full p-2 text-muted-foreground hover:bg-secondary hover:text-foreground lg:hidden"
            @click="isMobileNavOpen = !isMobileNavOpen"
          >
            <Icon :icon="isMobileNavOpen ? 'lucide:x' : 'lucide:menu'" class="h-4 w-4" />
          </button>
        </div>
      </div>
    </header>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isMobileNavOpen" class="fixed inset-x-4 top-20 z-40 rounded-3xl border border-border bg-card/95 p-3 shadow-2xl backdrop-blur-xl lg:hidden">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold',
            isCurrentRoute(item.path) ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
          ]"
          @click="isMobileNavOpen = false"
        >
          <Icon :icon="item.icon" class="h-4 w-4" />
          {{ item.name }}
        </router-link>
      </div>
    </Transition>

    <main class="relative mx-auto w-full max-w-7xl flex-1 px-4 pb-12 pt-8 sm:px-6 lg:px-8 lg:pt-12">
      <div class="pointer-events-none absolute inset-x-0 top-0 -z-10 h-96 overflow-hidden">
        <div class="absolute left-1/4 top-0 h-64 w-64 rounded-full bg-orange-500/10 blur-3xl" />
        <div class="absolute right-1/4 top-12 h-56 w-56 rounded-full bg-amber-500/10 blur-3xl" />
      </div>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-primary/80">AI career builder</p>
          <h1 class="mt-1 text-xl font-bold tracking-tight sm:text-2xl">{{ route.name || "AI Cover Letter Generator" }}</h1>
        </div>
        <span class="hidden items-center gap-1.5 text-[11px] text-muted-foreground sm:flex">
          <span :class="['h-1.5 w-1.5 rounded-full', health?.status === 'Connected' || health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500']" />
          {{ health?.config?.demo_mode ? "Demo mode" : "AI ready" }}
        </span>
      </div>
      <router-view />
    </main>
  </div>
</template>
