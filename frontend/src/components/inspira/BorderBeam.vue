<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  size?: number;
  duration?: number;
  borderWidth?: number;
  anchor?: number;
  colorFrom?: string;
  colorTo?: string;
  delay?: number;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  size: 200,
  duration: 12,
  anchor: 90,
  borderWidth: 1.5,
  colorFrom: "#3b82f6",
  colorTo: "#8b5cf6",
  delay: 0
});
</script>

<template>
  <div
    :style="{
      '--size': `${props.size}px`,
      '--duration': `${props.duration}s`,
      '--anchor': `${props.anchor}%`,
      '--border-width': `${props.borderWidth}px`,
      '--color-from': props.colorFrom,
      '--color-to': props.colorTo,
      '--delay': `-${props.delay}s`
    }"
    :class="
      cn(
        'pointer-events-none absolute inset-0 rounded-[inherit] [border:calc(var(--border-width))_solid_transparent]',
        '![mask-clip:padding-box,border-box] ![mask-composite:intersect] [mask:linear-gradient(transparent,transparent),linear-gradient(white,white)]',
        'after:absolute after:aspect-square after:w-[var(--size)] after:animate-border-beam after:[animation-delay:var(--delay)] after:[background:linear-gradient(to_left,var(--color-from),var(--color-to),transparent)] after:[offset-anchor:calc(var(--anchor))_50%] after:[offset-path:rect(0_auto_auto_0_round_calc(var(--size)))]',
        props.className
      )
    "
  />
</template>
