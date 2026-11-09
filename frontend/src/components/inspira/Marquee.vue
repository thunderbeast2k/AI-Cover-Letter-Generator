<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  reverse?: boolean;
  pauseOnHover?: boolean;
  vertical?: boolean;
  repeat?: number;
  duration?: string;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  reverse: false,
  pauseOnHover: true,
  vertical: false,
  repeat: 4,
  duration: "28s"
});
</script>

<template>
  <div
    :class="
      cn(
        'group flex overflow-hidden p-1.5 [--gap:1rem] [gap:var(--gap)]',
        {
          'flex-row': !props.vertical,
          'flex-col': props.vertical
        },
        props.className
      )
    "
    :style="{ '--duration': props.duration }"
  >
    <div
      v-for="index in props.repeat"
      :key="index"
      :class="
        cn('flex shrink-0 justify-around [gap:var(--gap)]', {
          'animate-marquee flex-row': !props.vertical,
          'group-hover:[animation-play-state:paused]': props.pauseOnHover,
          '[animation-direction:reverse]': props.reverse
        })
      "
    >
      <slot />
    </div>
  </div>
</template>

