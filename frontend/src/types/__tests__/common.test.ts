import { describe, expect, it } from "vitest";

import { MOOD_EMOJI, MOOD_LABEL, MOOD_OPTIONS } from "../common";

describe("mood constants", () => {
  it("defines exactly the 8 moods the spec requires", () => {
    expect(MOOD_OPTIONS).toHaveLength(8);
  });

  it("MOOD_EMOJI and MOOD_LABEL stay in sync with MOOD_OPTIONS", () => {
    for (const option of MOOD_OPTIONS) {
      expect(MOOD_EMOJI[option.value]).toBe(option.emoji);
      expect(MOOD_LABEL[option.value]).toBe(option.label);
    }
  });

  it("every mood value is unique", () => {
    const values = MOOD_OPTIONS.map((o) => o.value);
    expect(new Set(values).size).toBe(values.length);
  });
});
