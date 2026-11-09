import { ref } from "vue";
import type { CoverLetterDraft } from "@/types";

const STORAGE_KEY = "ai_cover_letter_drafts_v1";

export function useDrafts() {
  const drafts = ref<CoverLetterDraft[]>(loadDraftsFromStorage());

  function loadDraftsFromStorage(): CoverLetterDraft[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      return JSON.parse(raw);
    } catch (err) {
      console.warn("Failed to read drafts from localStorage:", err);
      return [];
    }
  }

  function persistDrafts() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts.value));
    } catch (err) {
      console.warn("Failed to persist drafts to localStorage:", err);
    }
  }

  function getDrafts(): CoverLetterDraft[] {
    drafts.value = loadDraftsFromStorage();
    return drafts.value;
  }

  function getDraft(id: string): CoverLetterDraft | undefined {
    return drafts.value.find((d) => d.id === id);
  }

  function saveDraft(
    data: Omit<CoverLetterDraft, "id" | "created_at" | "updated_at"> & { id?: string }
  ): CoverLetterDraft {
    const now = new Date().toISOString();
    let draft: CoverLetterDraft;

    if (data.id) {
      const idx = drafts.value.findIndex((d) => d.id === data.id);
      if (idx !== -1) {
        draft = {
          ...drafts.value[idx],
          ...data,
          id: data.id,
          updated_at: now
        };
        drafts.value[idx] = draft;
      } else {
        draft = {
          ...data,
          id: data.id,
          created_at: now,
          updated_at: now
        };
        drafts.value.unshift(draft);
      }
    } else {
      draft = {
        ...data,
        id: "draft_" + Math.random().toString(36).substring(2, 10),
        created_at: now,
        updated_at: now
      };
      drafts.value.unshift(draft);
    }

    persistDrafts();
    return draft;
  }

  function deleteDraft(id: string): boolean {
    const initialLen = drafts.value.length;
    drafts.value = drafts.value.filter((d) => d.id !== id);
    if (drafts.value.length !== initialLen) {
      persistDrafts();
      return true;
    }
    return false;
  }

  function duplicateDraft(id: string): CoverLetterDraft | undefined {
    const original = drafts.value.find((d) => d.id === id);
    if (!original) return undefined;

    const copy: CoverLetterDraft = {
      ...original,
      id: "draft_" + Math.random().toString(36).substring(2, 10),
      title: `${original.title} (Copy)`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    drafts.value.unshift(copy);
    persistDrafts();
    return copy;
  }

  function renameDraft(id: string, newTitle: string): boolean {
    const draft = drafts.value.find((d) => d.id === id);
    if (draft) {
      draft.title = newTitle.trim();
      draft.updated_at = new Date().toISOString();
      persistDrafts();
      return true;
    }
    return false;
  }

  function clearAllDrafts() {
    drafts.value = [];
    localStorage.removeItem(STORAGE_KEY);
  }

  return {
    drafts,
    getDrafts,
    getDraft,
    saveDraft,
    deleteDraft,
    duplicateDraft,
    renameDraft,
    clearAllDrafts
  };
}
