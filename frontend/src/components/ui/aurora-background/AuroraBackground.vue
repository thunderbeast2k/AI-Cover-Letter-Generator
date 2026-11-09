<script setup lang="ts">
import AuroraBackground from "@/components/inspira/AuroraBackground.vue";

interface AuroraBackgroundProps {
  radialGradient?: boolean;
  class?: string;
  className?: string;
}

const props = defineProps<AuroraBackgroundProps>();
</script>

<template>
  <AuroraBackground v-bind="props">
    <slot />
  </AuroraBackground>
</template>

