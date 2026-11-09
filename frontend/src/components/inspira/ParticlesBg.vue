<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { cn } from "@/utils/cn";

interface Props {
  className?: string;
  quantity?: number;
  staticity?: number;
  ease?: number;
  color?: string;
}

const props = withDefaults(defineProps<Props>(), {
  className: "",
  quantity: 40,
  staticity: 50,
  ease: 50,
  color: "#3b82f6"
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number;

interface Particle {
  x: number;
  y: number;
  translateX: number;
  translateY: number;
  size: number;
  alpha: number;
  targetAlpha: number;
  dx: number;
  dy: number;
  magnetism: number;
}

let particles: Particle[] = [];
let dpr = 1;

const initParticles = (width: number, height: number) => {
  particles = [];
  for (let i = 0; i < props.quantity; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      translateX: 0,
      translateY: 0,
      size: Math.random() * 2 + 1,
      alpha: Math.random() * 0.4 + 0.1,
      targetAlpha: Math.random() * 0.4 + 0.1,
      dx: (Math.random() - 0.5) * 0.3,
      dy: (Math.random() - 0.5) * 0.3,
      magnetism: 0.1 + Math.random() * 4
    });
  }
};

const render = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  particles.forEach((p) => {
    p.x += p.dx;
    p.y += p.dy;

    if (p.x < 0) p.x = canvas.width / dpr;
    if (p.x > canvas.width / dpr) p.x = 0;
    if (p.y < 0) p.y = canvas.height / dpr;
    if (p.y > canvas.height / dpr) p.y = 0;

    ctx.save();
    ctx.beginPath();
    ctx.arc(p.x * dpr, p.y * dpr, p.size * dpr, 0, 2 * Math.PI);
    ctx.fillStyle = props.color;
    ctx.globalAlpha = p.alpha;
    ctx.fill();
    ctx.restore();
  });

  animationFrameId = requestAnimationFrame(render);
};

const resize = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  initParticles(rect.width, rect.height);
};

onMounted(() => {
  resize();
  window.addEventListener("resize", resize);
  render();
});

onUnmounted(() => {
  window.removeEventListener("resize", resize);
  cancelAnimationFrame(animationFrameId);
});
</script>

<template>
  <div :class="cn('pointer-events-none absolute inset-0 overflow-hidden', props.className)">
    <canvas ref="canvasRef" class="h-full w-full" />
  </div>
</template>
