<script setup lang="ts">
import { useId } from "vue";
import { cn } from "@/utils/cn";

interface Props {
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  cx?: number;
  cy?: number;
  cr?: number;
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  width: 20,
  height: 20,
  x: 0,
  y: 0,
  cx: 1,
  cy: 1,
  cr: 1,
  className: ""
});

const id = useId();
</script>

<template>
  <svg
    aria-hidden="true"
    :class="
      cn(
        'pointer-events-none absolute inset-0 h-full w-full fill-neutral-400/25 [mask-image:radial-gradient(ellipse_at_center,white_35%,transparent_80%)] dark:fill-neutral-500/20',
        props.className
      )
    "
  >
    <defs>
      <pattern
        :id="`dot-pattern-${id}`"
        :width="props.width"
        :height="props.height"
        patternUnits="userSpaceOnUse"
        patternContentUnits="userSpaceOnUse"
        :x="props.x"
        :y="props.y"
      >
        <circle
          :cx="props.cx"
          :cy="props.cy"
          :r="props.cr"
        />
      </pattern>
    </defs>
    <rect
      width="100%"
      height="100%"
      stroke-width="0"
      :fill="`url(#dot-pattern-${id})`"
    />
  </svg>
</template>

