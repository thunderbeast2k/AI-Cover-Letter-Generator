<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  shimmerColor?: string;
  shimmerSize?: string;
  borderRadius?: string;
  shimmerDuration?: string;
  background?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  shimmerColor: "#ffffff",
  shimmerSize: "0.1em",
  shimmerDuration: "2.5s",
  borderRadius: "0.625rem",
  background: "rgba(37, 99, 235, 1)",
  disabled: false
});

const emit = defineEmits<{
  (e: "click", event: MouseEvent): void;
}>();
</script>

<template>
  <button
    :disabled="props.disabled"
    :style="{
      '--spread': '90deg',
      '--shimmer-color': props.shimmerColor,
      '--radius': props.borderRadius,
      '--speed': props.shimmerDuration,
      '--cut': props.shimmerSize,
      '--bg': props.background
    }"
    :class="
      cn(
        'group relative z-0 flex cursor-pointer items-center justify-center overflow-hidden whitespace-nowrap px-5 py-2.5 text-white [background:var(--bg)] [border-radius:var(--radius)] transition-all duration-300 hover:scale-[1.01] active:scale-[0.98] disabled:pointer-events-none disabled:opacity-60',
        props.className
      )
    "
    @click="(e) => emit('click', e)"
  >
    <!-- Spark / Shimmer container -->
    <div
      class="-z-30 blur-[2px] absolute inset-0 overflow-visible [container-type:size]"
    >
      <div
        class="absolute inset-0 h-[100cqh] animate-slide [aspect-ratio:1] [border-radius:0] [mask:none]"
      >
        <div
          class="animate-spin-around absolute inset-[-100%] w-auto rotate-0 [background:conic-gradient(from_calc(270deg-(var(--spread)*0.5)),transparent_0,var(--shimmer-color)_var(--spread),transparent_var(--spread))] [translate:0_0]"
        />
      </div>
    </div>
    <!-- Inner backdrop -->
    <div
      class="absolute [background:var(--bg)] [border-radius:var(--radius)] [inset:var(--cut)] -z-20"
    />
    <slot />
  </button>
</template>

<style scoped>
@keyframes spin-around {
  0% {
    transform: translateZ(0) rotate(0);
  }
  100% {
    transform: translateZ(0) rotate(360deg);
  }
}

.animate-spin-around {
  animation: spin-around var(--speed) linear infinite;
}
</style>
