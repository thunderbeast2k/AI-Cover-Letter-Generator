<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { TEMPLATES } from "@/utils/templates";
import { useToast } from "@/composables/useToast";
import Badge from "@/components/common/Badge.vue";
import CardSpotlight from "@/components/inspira/CardSpotlight.vue";
import DotPattern from "@/components/inspira/DotPattern.vue";

const router = useRouter();
const { success } = useToast();

const previewTemplate = (templateId: string) => {
  router.push({ path: "/workspace", query: { template: templateId } });
  success(`Template selected: ${templateId}`);
};
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="relative overflow-hidden rounded-2xl border border-border bg-card/60 p-6 shadow-xs">
      <DotPattern class="opacity-30" />
      <div class="relative z-10">
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Icon icon="lucide:layout-template" class="h-6 w-6 text-primary" />
          Document Templates
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          Explore 5 professionally designed layout architectures calibrated for corporate, tech, and early-career job applications.
        </p>
      </div>
    </div>

    <!-- Templates Gallery Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="tmpl in TEMPLATES"
        :key="tmpl.id"
        class="group rounded-3xl border border-border bg-card overflow-hidden shadow-sm hover:border-primary/50 transition-all flex flex-col justify-between"
      >
        <!-- Mock Paper Header Preview -->
        <div class="bg-muted/40 p-5 border-b border-border/80 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
              Layout Preview
            </span>
            <Badge variant="outline" class="text-[10px]">
              {{ tmpl.badge }}
            </Badge>
          </div>

          <!-- Abstract Document Paper Illustration -->
          <div class="rounded-xl border border-border/80 bg-background p-4 shadow-sm space-y-2.5">
            <!-- Header layout simulation -->
            <div
              :class="[
                'space-y-1',
                tmpl.id === 'minimal' ? 'text-center' : 'text-left'
              ]"
            >
              <div
                :class="[
                  'h-3 bg-foreground/80 rounded w-1/3',
                  tmpl.id === 'minimal' ? 'mx-auto' : ''
                ]"
              />
              <div
                :class="[
                  'h-1.5 bg-muted-foreground/40 rounded w-1/2',
                  tmpl.id === 'minimal' ? 'mx-auto' : ''
                ]"
              />
            </div>

            <!-- Divider line -->
            <div
              :class="[
                'h-0.5 w-full rounded',
                tmpl.id === 'technical' ? 'bg-primary' : 'bg-border'
              ]"
            />

            <!-- Body lines simulation -->
            <div class="space-y-1.5 pt-1">
              <div class="h-2 bg-muted/60 rounded w-1/4" />
              <div class="h-2 bg-muted/80 rounded w-full" />
              <div class="h-2 bg-muted/80 rounded w-5/6" />
              <div class="h-2 bg-muted/80 rounded w-4/5" />
            </div>

            <div class="space-y-1.5 pt-1">
              <div class="h-2 bg-muted/80 rounded w-full" />
              <div class="h-2 bg-muted/80 rounded w-3/4" />
            </div>
          </div>
        </div>

        <!-- Template Information -->
        <div class="p-6 space-y-4 flex-1 flex flex-col justify-between">
          <div class="space-y-2">
            <h3 class="text-base font-bold text-foreground flex items-center gap-2">
              {{ tmpl.name }}
            </h3>
            <p class="text-xs text-muted-foreground leading-relaxed">
              {{ tmpl.description }}
            </p>
          </div>

          <div class="space-y-3 pt-2">
            <div class="text-[11px] text-muted-foreground/90">
              <span class="font-semibold text-foreground">Target Role Scope:</span>
              <p class="mt-0.5">{{ tmpl.suitableFor }}</p>
            </div>

            <button
              class="w-full rounded-xl bg-primary/10 text-primary hover:bg-primary hover:text-white py-2.5 text-xs font-semibold transition-all flex items-center justify-center gap-1.5 group-hover:scale-[1.01]"
              @click="previewTemplate(tmpl.id)"
            >
              <span>Use {{ tmpl.name }}</span>
              <Icon icon="lucide:arrow-right" class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
