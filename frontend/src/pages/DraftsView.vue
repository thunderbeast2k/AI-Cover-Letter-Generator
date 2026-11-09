<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";
import { useDrafts } from "@/composables/useDrafts";
import { useToast } from "@/composables/useToast";
import Badge from "@/components/common/Badge.vue";
import type { CoverLetterDraft } from "@/types";

const router = useRouter();
const { getDrafts, deleteDraft, duplicateDraft, renameDraft, clearAllDrafts } = useDrafts();
const { success, error, info } = useToast();

const draftsList = ref<CoverLetterDraft[]>([]);
const editingDraftId = ref<string | null>(null);
const newTitleText = ref("");

const refresh = () => {
  draftsList.value = getDrafts();
};

onMounted(() => {
  refresh();
});

const openInWorkspace = (id: string) => {
  router.push({ path: "/workspace", query: { draftId: id } });
};

const handleDelete = (id: string, title: string) => {
  if (confirm(`Are you sure you want to delete the draft "${title}"?`)) {
    deleteDraft(id);
    refresh();
    success(`Draft "${title}" deleted.`);
  }
};

const handleDuplicate = (id: string) => {
  const copy = duplicateDraft(id);
  if (copy) {
    refresh();
    success(`Duplicated draft: "${copy.title}"`);
  }
};

const startRenaming = (draft: CoverLetterDraft) => {
  editingDraftId.value = draft.id;
  newTitleText.value = draft.title;
};

const saveRename = (id: string) => {
  if (!newTitleText.value.trim()) return;
  renameDraft(id, newTitleText.value.trim());
  editingDraftId.value = null;
  refresh();
  success("Draft renamed.");
};

const handleClearAll = () => {
  if (confirm("Are you sure you want to clear all locally saved drafts? This cannot be undone.")) {
    clearAllDrafts();
    refresh();
    info("All drafts cleared from browser local storage.");
  }
};

const formatDate = (iso: string) => {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch {
    return iso;
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b pb-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <Icon icon="lucide:bookmark" class="h-6 w-6 text-primary" />
          My Saved Drafts
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          Locally saved cover letters stored in your browser's private local storage.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-if="draftsList.length > 0"
          class="text-xs text-muted-foreground hover:text-destructive flex items-center gap-1 px-3 py-1.5 rounded-lg border hover:bg-destructive/10 transition-colors"
          @click="handleClearAll"
        >
          <Icon icon="lucide:trash" class="h-3.5 w-3.5" />
          <span>Clear All Drafts</span>
        </button>

        <router-link
          to="/workspace"
          class="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-primary/90 transition-all"
        >
          <Icon icon="lucide:plus" class="h-3.5 w-3.5" />
          <span>New Letter</span>
        </router-link>
      </div>
    </div>

    <!-- Storage Privacy Notice -->
    <div class="rounded-xl border border-blue-500/20 bg-blue-50/50 dark:bg-blue-950/20 p-4 text-xs text-muted-foreground flex items-start gap-3">
      <Icon icon="lucide:shield-check" class="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
      <div>
        <span class="font-semibold text-foreground">Privacy by Architecture:</span>
        Drafts and resume text remain stored strictly on your local browser. They are never retained in a backend database or shared with external analytics.
      </div>
    </div>

    <!-- Drafts Grid -->
    <div v-if="draftsList.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div
        v-for="draft in draftsList"
        :key="draft.id"
        class="group rounded-2xl border border-border bg-card p-5 shadow-sm hover:border-primary/50 transition-all flex flex-col justify-between space-y-4"
      >
        <div class="space-y-3">
          <!-- Top Row: Style & Date -->
          <div class="flex items-center justify-between text-[11px]">
            <Badge variant="outline" class="capitalize">
              {{ draft.writing_style }}
            </Badge>
            <span class="text-muted-foreground">
              {{ formatDate(draft.updated_at) }}
            </span>
          </div>

          <!-- Title (or inline rename input) -->
          <div v-if="editingDraftId === draft.id" class="flex items-center gap-2">
            <input
              v-model="newTitleText"
              type="text"
              class="w-full rounded-lg border border-input bg-background px-2.5 py-1 text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              @keydown.enter="saveRename(draft.id)"
            />
            <button
              class="p-1 text-emerald-500 hover:text-emerald-600"
              @click="saveRename(draft.id)"
            >
              <Icon icon="lucide:check" class="h-4 w-4" />
            </button>
            <button
              class="p-1 text-muted-foreground hover:text-foreground"
              @click="editingDraftId = null"
            >
              <Icon icon="lucide:x" class="h-4 w-4" />
            </button>
          </div>

          <div v-else class="flex items-start justify-between gap-2">
            <h3
              class="text-sm font-bold text-foreground group-hover:text-primary transition-colors cursor-pointer line-clamp-1"
              @click="openInWorkspace(draft.id)"
            >
              {{ draft.title }}
            </h3>
            <button
              class="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-foreground p-0.5 rounded transition-opacity"
              title="Rename draft"
              @click="startRenaming(draft)"
            >
              <Icon icon="lucide:edit-2" class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Letter Excerpt -->
          <p
            class="text-xs text-muted-foreground line-clamp-3 leading-relaxed cursor-pointer font-sans"
            @click="openInWorkspace(draft.id)"
          >
            {{ draft.cover_letter }}
          </p>
        </div>

        <!-- Footer Actions -->
        <div class="pt-3 border-t border-border/60 flex items-center justify-between text-xs">
          <span class="text-muted-foreground font-medium text-[11px] truncate max-w-[120px]">
            {{ draft.job_info.company_name || 'General' }}
          </span>

          <div class="flex items-center gap-1.5">
            <!-- Duplicate button -->
            <button
              class="rounded-lg p-1.5 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
              title="Duplicate draft"
              @click="handleDuplicate(draft.id)"
            >
              <Icon icon="lucide:copy" class="h-4 w-4" />
            </button>

            <!-- Delete button -->
            <button
              class="rounded-lg p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              title="Delete draft"
              @click="handleDelete(draft.id, draft.title)"
            >
              <Icon icon="lucide:trash-2" class="h-4 w-4" />
            </button>

            <!-- Open in Workspace -->
            <button
              class="rounded-lg bg-primary/10 text-primary px-2.5 py-1 font-semibold hover:bg-primary hover:text-white transition-colors flex items-center gap-1"
              @click="openInWorkspace(draft.id)"
            >
              <span>Open</span>
              <Icon icon="lucide:arrow-right" class="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="rounded-2xl border border-dashed border-border p-12 text-center bg-card/40 space-y-3"
    >
      <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary text-muted-foreground mx-auto">
        <Icon icon="lucide:bookmark" class="h-7 w-7" />
      </div>
      <h3 class="text-base font-semibold text-foreground">
        No Saved Drafts Yet
      </h3>
      <p class="text-xs text-muted-foreground max-w-sm mx-auto leading-relaxed">
        When generating or editing letters in the Cover Letter Workspace, click "Save Draft" to store your progress here.
      </p>
      <router-link
        to="/workspace"
        class="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-primary/90 transition-all mt-2"
      >
        <Icon icon="lucide:pen-tool" class="h-3.5 w-3.5" />
        <span>Go to Workspace</span>
      </router-link>
    </div>
  </div>
</template>
