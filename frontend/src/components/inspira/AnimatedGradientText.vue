<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  speed?: number;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  speed: 4
});
</script>

<template>
  <div
    :class="
      cn(
        'group relative inline-flex items-center justify-center rounded-full border border-border/80 bg-card/80 px-3.5 py-1 text-xs font-semibold backdrop-blur-md transition-all duration-300 hover:border-primary/40 hover:shadow-[0_0_20px_-5px_rgba(59,130,246,0.25)]',
        props.className
      )
    "
  >
    <div
      class="inline-flex items-center gap-1.5 bg-gradient-to-r from-blue-500 via-violet-500 via-pink-500 to-blue-500 bg-clip-text text-transparent animate-gradient-text font-bold"
    >
      <slot />
    </div>
  </div>
</template>

