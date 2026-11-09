<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: "md",
  className: "",
  label: ""
});

const sizeClasses = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-10 w-10 border-3"
};
</script>

<template>
  <div :class="cn('flex items-center justify-center gap-2', props.className)">
    <div
      :class="
        cn(
          'animate-spin rounded-full border-primary border-t-transparent',
          sizeClasses[props.size]
        )
      "
    />
    <span v-if="props.label" class="text-xs font-medium text-muted-foreground">
      {{ props.label }}
    </span>
  </div>
</template>
