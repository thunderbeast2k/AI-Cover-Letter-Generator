import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import LiveDocumentEditor from "../src/components/editor/LiveDocumentEditor.vue";

describe("LiveDocumentEditor Component", () => {
  const samplePersonalInfo = {
    full_name: "Sarah Connors",
    email: "sarah@example.com",
    phone: "555-0199",
    location: "Los Angeles, CA"
  };

  const sampleJobInfo = {
    job_title: "DevOps Engineer",
    company_name: "Cyberdyne Systems",
    job_description: "Build distributed clouds",
    application_type: "Full-time"
  };

  it("renders applicant header and calculates word count correctly", async () => {
    const text = "Dear Hiring Team,\n\nI am writing to express my enthusiasm for the DevOps Engineer position. I bring hands-on experience in cloud architecture.\n\nSincerely,\nSarah";
    
    const wrapper = mount(LiveDocumentEditor, {
      props: {
        coverLetter: text,
        personalInfo: samplePersonalInfo,
        jobInfo: sampleJobInfo,
        templateId: "classic",
        isGenerating: false
      }
    });

    expect(wrapper.text()).toContain("Sarah Connors");
    expect(wrapper.text()).toContain("words");

    const textarea = wrapper.find("textarea");
    expect(textarea.element.value).toBe(text);
  });

  it("emits update:coverLetter when user types in editor", async () => {
    const wrapper = mount(LiveDocumentEditor, {
      props: {
        coverLetter: "Initial text",
        personalInfo: samplePersonalInfo,
        jobInfo: sampleJobInfo,
        templateId: "classic",
        isGenerating: false
      }
    });

    const textarea = wrapper.find("textarea");
    await textarea.setValue("Updated cover letter content");

    expect(wrapper.emitted()["update:coverLetter"]).toBeTruthy();
    expect(wrapper.emitted()["update:coverLetter"][0]).toEqual(["Updated cover letter content"]);
  });
});
