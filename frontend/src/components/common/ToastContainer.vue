<script setup lang="ts">
import { useToast } from "@/composables/useToast";
import { Icon } from "@iconify/vue";

const { toasts, removeToast } = useToast();

const getIcon = (type: string) => {
  switch (type) {
    case "success":
      return "lucide:check-circle-2";
    case "error":
      return "lucide:alert-circle";
    case "warning":
      return "lucide:alert-triangle";
    default:
      return "lucide:info";
  }
};

const getColors = (type: string) => {
  switch (type) {
    case "success":
      return "border-emerald-500/30 bg-emerald-50/90 text-emerald-950 dark:bg-emerald-950/80 dark:text-emerald-100";
    case "error":
      return "border-rose-500/30 bg-rose-50/90 text-rose-950 dark:bg-rose-950/80 dark:text-rose-100";
    case "warning":
      return "border-amber-500/30 bg-amber-50/90 text-amber-950 dark:bg-amber-950/80 dark:text-amber-100";
    default:
      return "border-blue-500/30 bg-blue-50/90 text-blue-950 dark:bg-blue-950/80 dark:text-blue-100";
  }
};
</script>

<template>
  <div
    class="pointer-events-none fixed bottom-4 right-4 z-50 flex max-w-md flex-col gap-2 p-2"
  >
    <TransitionGroup
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'pointer-events-auto flex items-start gap-3 rounded-xl border p-4 shadow-lg backdrop-blur-md',
          getColors(toast.type)
        ]"
      >
        <Icon :icon="getIcon(toast.type)" class="mt-0.5 h-5 w-5 shrink-0" />
        <div class="flex-1">
          <h4 v-if="toast.title" class="text-sm font-semibold">
            {{ toast.title }}
          </h4>
          <p class="text-xs opacity-90">
            {{ toast.message }}
          </p>
        </div>
        <button
          class="shrink-0 rounded p-1 opacity-70 hover:opacity-100"
          @click="removeToast(toast.id)"
        >
          <Icon icon="lucide:x" class="h-4 w-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
