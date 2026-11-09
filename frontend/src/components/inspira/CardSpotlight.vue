<script setup lang="ts">
import { ref } from "vue";
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  gradientSize?: number;
  gradientColor?: string;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  gradientSize: 300,
  gradientColor: "#3b82f6"
});

const mouseX = ref(-1000);
const mouseY = ref(-1000);
const isHovered = ref(false);

const handleMouseMove = (e: MouseEvent) => {
  const target = e.currentTarget as HTMLElement;
  const rect = target.getBoundingClientRect();
  mouseX.value = e.clientX - rect.left;
  mouseY.value = e.clientY - rect.top;
};

const handleMouseEnter = () => {
  isHovered.value = true;
};

const handleMouseLeave = () => {
  isHovered.value = false;
  mouseX.value = -1000;
  mouseY.value = -1000;
};
</script>

<template>
  <div
    :class="
      cn(
        'group relative overflow-hidden rounded-xl border border-border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md',
        props.className
      )
    "
    @mousemove="handleMouseMove"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Spotlight gradient overlay -->
    <div
      class="pointer-events-none absolute -inset-px rounded-xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      :style="{
        background: `radial-gradient(${props.gradientSize}px circle at ${mouseX}px ${mouseY}px, ${props.gradientColor}18, transparent 80%)`
      }"
    />
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>
