<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/utils/cn";

interface Props {
  count?: number;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  count: 15,
  className: ""
});

const meteors = computed(() => {
  return Array.from({ length: props.count }, (_, i) => ({
    id: i,
    top: `${Math.floor(Math.random() * 80)}%`,
    left: `${Math.floor(Math.random() * 95)}%`,
    animationDelay: `${(Math.random() * 1.5 + 0.2).toFixed(2)}s`,
    animationDuration: `${Math.floor(Math.random() * 6 + 4)}s`
  }));
});
</script>

<template>
  <div :class="cn('pointer-events-none absolute inset-0 overflow-hidden', props.className)">
    <span
      v-for="m in meteors"
      :key="m.id"
      :style="{
        top: m.top,
        left: m.left,
        animationDelay: m.animationDelay,
        animationDuration: m.animationDuration
      }"
      class="pointer-events-none absolute h-0.5 w-0.5 rotate-[215deg] animate-meteor rounded-[9999px] bg-blue-400 shadow-[0_0_0_1px_#ffffff20] before:absolute before:top-1/2 before:h-[1px] before:w-[50px] before:-translate-y-1/2 before:bg-gradient-to-r before:from-blue-400 before:to-transparent before:content-['']"
    />
  </div>
</template>

