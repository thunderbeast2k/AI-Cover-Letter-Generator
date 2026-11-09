<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { useDrafts } from "@/composables/useDrafts";
import type { CoverLetterDraft } from "@/types";

const router = useRouter();
const { getDrafts } = useDrafts();
const recentDrafts = ref<CoverLetterDraft[]>([]);

const capabilities = [
  { title: "Generate with context", copy: "Turn a resume and job description into a clear, personal first draft.", icon: "lucide:sparkles" },
  { title: "Find your advantage", copy: "Surface the skills, keywords, and achievements that matter most.", icon: "lucide:wand-sparkles" },
  { title: "Polish with confidence", copy: "Check tone, clarity, and ATS readiness before you apply.", icon: "lucide:badge-check" }
];

onMounted(() => { recentDrafts.value = getDrafts().slice(0, 3); });
const openDraft = (id: string) => router.push({ path: "/workspace", query: { draftId: id } });
const formatDate = (iso: string) => new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
</script>

<template>
  <div class="space-y-12">
    <section class="buildify-hero relative overflow-hidden rounded-[2rem] px-6 py-14 text-white sm:px-12 sm:py-20">
      <div class="buildify-noise absolute inset-0 opacity-20" />
      <div class="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-orange-400/20 blur-3xl" />
      <div class="relative z-10 max-w-3xl">
        <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-orange-200/20 bg-white/10 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.22em] text-orange-100">
          <Icon icon="lucide:sparkles" class="h-3.5 w-3.5" /> AI-powered career builder
        </div>
        <h2 class="max-w-3xl text-4xl font-semibold leading-[1.03] tracking-[-0.06em] sm:text-6xl">
          Build a career story that <span class="buildify-gradient-text">gets noticed.</span>
        </h2>
        <p class="mt-6 max-w-xl text-sm leading-7 text-orange-100/70 sm:text-base">
          From your first idea to a ready-to-send application, CareerCraft uses AI to help you write, refine, and launch your next move in minutes.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <button class="buildify-button flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold" @click="router.push('/workspace')">
            Build my cover letter <Icon icon="lucide:arrow-up-right" class="h-4 w-4" />
          </button>
          <router-link to="/analyzer" class="flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-5 py-3 text-sm font-semibold hover:bg-white/10">
            Analyze a job <Icon icon="lucide:scan-search" class="h-4 w-4 text-orange-200" />
          </router-link>
        </div>
      </div>
      <p class="absolute bottom-7 right-8 hidden text-xs text-orange-100/50 sm:block">Built for ambitious applicants.</p>
    </section>

    <section class="flex flex-wrap items-center justify-between gap-4 border-y border-border py-5">
      <p class="text-xs font-semibold text-muted-foreground">Trusted by candidates building their next chapter</p>
      <div class="flex items-center gap-6 text-xs font-bold tracking-tight text-muted-foreground/60 sm:gap-10">
        <span>STARTUPS</span><span>STUDIOS</span><span>PRODUCT</span><span>ENGINEERING</span>
      </div>
    </section>

    <section>
      <div class="max-w-xl">
        <p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-primary">Everything you need</p>
        <h3 class="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">Fast. Intelligent. Built for your next opportunity.</h3>
      </div>
      <div class="mt-8 grid gap-4 md:grid-cols-3">
        <router-link v-for="(capability, index) in capabilities" :key="capability.title" :to="index === 0 ? '/workspace' : index === 1 ? '/matching' : '/settings'" class="group rounded-3xl border border-border bg-card/70 p-6 transition-all hover:-translate-y-1 hover:border-primary/40 hover:shadow-xl">
          <div class="flex items-center justify-between">
            <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary"><Icon :icon="capability.icon" class="h-5 w-5" /></span>
            <span class="text-xs font-semibold text-muted-foreground/50">0{{ index + 1 }}</span>
          </div>
          <h4 class="mt-10 font-semibold">{{ capability.title }}</h4>
          <p class="mt-2 text-sm leading-6 text-muted-foreground">{{ capability.copy }}</p>
          <span class="mt-6 inline-flex items-center gap-1 text-xs font-semibold text-primary">Explore <Icon icon="lucide:arrow-up-right" class="h-3.5 w-3.5 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" /></span>
        </router-link>
      </div>
    </section>

    <section class="rounded-3xl border border-border bg-card/60 p-6 sm:p-8">
      <div class="flex items-center justify-between">
        <div><p class="text-[10px] font-semibold uppercase tracking-[0.24em] text-primary">Your workspace</p><h3 class="mt-2 text-xl font-bold tracking-tight">Recent drafts</h3></div>
        <router-link to="/drafts" class="text-xs font-semibold text-primary hover:underline">View all</router-link>
      </div>
      <div v-if="recentDrafts.length" class="mt-6 grid gap-3 md:grid-cols-3">
        <button v-for="draft in recentDrafts" :key="draft.id" class="rounded-2xl border border-border bg-background/50 p-4 text-left transition-colors hover:border-primary/40" @click="openDraft(draft.id)">
          <div class="flex items-center justify-between gap-3"><span class="truncate text-sm font-semibold">{{ draft.title }}</span><Icon icon="lucide:arrow-up-right" class="h-4 w-4 shrink-0 text-muted-foreground" /></div>
          <p class="mt-3 text-xs text-muted-foreground">{{ formatDate(draft.updated_at) }}</p>
        </button>
      </div>
      <div v-else class="mt-6 rounded-2xl border border-dashed border-border p-8 text-center"><p class="text-sm font-medium">Your first great letter starts here.</p><router-link to="/workspace" class="mt-3 inline-flex text-xs font-semibold text-primary hover:underline">Create a draft</router-link></div>
    </section>

    <section class="rounded-[2rem] bg-primary px-6 py-12 text-center text-primary-foreground sm:px-12">
      <p class="text-[10px] font-semibold uppercase tracking-[0.24em] opacity-70">Ready when you are</p>
      <h3 class="mx-auto mt-3 max-w-2xl text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">Turn your experience into your next opportunity.</h3>
      <router-link to="/workspace" class="mt-7 inline-flex items-center gap-2 rounded-full bg-background px-5 py-3 text-sm font-semibold text-foreground hover:opacity-90">Start building <Icon icon="lucide:arrow-up-right" class="h-4 w-4" /></router-link>
    </section>
  </div>
</template>
