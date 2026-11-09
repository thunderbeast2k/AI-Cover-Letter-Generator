<script setup lang="ts">
import { cn } from "@/utils/cn";

interface Props {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "destructive";
  className?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "default",
  className: ""
});

const variantClasses = {
  default: "bg-primary text-primary-foreground hover:bg-primary/90",
  secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
  outline: "border border-border text-foreground",
  success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20",
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20",
  destructive: "bg-destructive/10 text-destructive border border-destructive/20"
};
</script>

<template>
  <span
    :class="
      cn(
        'inline-flex items-center gap-1 rounded-md px-2.5 py-0.5 text-xs font-medium transition-colors',
        variantClasses[props.variant],
        props.className
      )
    "
  >
    <slot />
  </span>
</template>
