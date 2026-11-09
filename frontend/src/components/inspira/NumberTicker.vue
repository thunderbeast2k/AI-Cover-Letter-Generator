<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { useTransition, TransitionPresets } from "@vueuse/core";
import { cn } from "@/utils/cn";

interface Props {
  value: number;
  duration?: number;
  delay?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
  decimalPlaces?: number;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 1500,
  delay: 0,
  className: "",
  prefix: "",
  suffix: "",
  decimalPlaces: 0
});

const source = ref(0);

const output = useTransition(source, {
  duration: props.duration,
  transition: TransitionPresets.easeOutCubic
});

const formattedValue = computed(() => {
  return `${props.prefix}${output.value.toFixed(props.decimalPlaces)}${props.suffix}`;
});

onMounted(() => {
  if (props.delay > 0) {
    setTimeout(() => {
      source.value = props.value;
    }, props.delay);
  } else {
    source.value = props.value;
  }
});

watch(
  () => props.value,
  (newVal) => {
    source.value = newVal;
  }
);
</script>

<template>
  <span :class="cn('inline-block tabular-nums font-bold tracking-tight', props.className)">
    {{ formattedValue }}
  </span>
</template>

