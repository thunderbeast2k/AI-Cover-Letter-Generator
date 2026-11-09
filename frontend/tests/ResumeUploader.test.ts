import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import ResumeUploader from "../src/components/resume/ResumeUploader.vue";

describe("ResumeUploader Component", () => {
  it("renders drag-and-drop dropzone prompt by default", () => {
    const wrapper = mount(ResumeUploader);
    expect(wrapper.text()).toContain("Upload your Resume");
    expect(wrapper.text()).toContain("PDF or DOCX");
    expect(wrapper.find("input[type='file']").exists()).toBe(true);
  });
});
