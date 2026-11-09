<script setup lang="ts">
import { computed } from "vue";
import { motion } from "motion-v";
import { cn } from "@/utils/cn";

interface Props {
  words: string;
  className?: string;
  delay?: number;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  delay: 0.04
});

const wordsArray = computed(() => {
  return props.words.split(" ");
});
</script>

<template>
  <div :class="cn('font-normal', props.className)">
    <span
      v-for="(word, idx) in wordsArray"
      :key="word + idx"
      class="inline-block"
    >
      <motion.span
        :initial="{ opacity: 0, y: 4, filter: 'blur(3px)' }"
        :animate="{ opacity: 1, y: 0, filter: 'blur(0px)' }"
        :transition="{
          duration: 0.4,
          delay: idx * props.delay,
          ease: 'easeOut'
        }"
        class="inline-block"
      >
        {{ word }}&nbsp;
      </motion.span>
    </span>
  </div>
</template>
