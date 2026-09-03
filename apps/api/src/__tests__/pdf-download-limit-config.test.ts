import { afterEach, describe, expect, it, vi } from "vitest";

const originalValue = process.env.PDF_DOWNLOAD_MAX_FILE_SIZE_MB;

async function loadLimit(value?: string): Promise<number> {
  vi.resetModules();
  if (value === undefined) {
    delete process.env.PDF_DOWNLOAD_MAX_FILE_SIZE_MB;
  } else {
    process.env.PDF_DOWNLOAD_MAX_FILE_SIZE_MB = value;
  }
  const { config } = await import("../config");
  return config.PDF_DOWNLOAD_MAX_FILE_SIZE_MB;
}

afterEach(() => {
  vi.resetModules();
  if (originalValue === undefined) {
    delete process.env.PDF_DOWNLOAD_MAX_FILE_SIZE_MB;
  } else {
    process.env.PDF_DOWNLOAD_MAX_FILE_SIZE_MB = originalValue;
  }
});

describe("PDF download size configuration", () => {
  it("keeps the conservative 50 MB default", async () => {
    await expect(loadLimit()).resolves.toBe(50);
  });

  it("allows a larger bounded limit for capable self-hosted machines", async () => {
    await expect(loadLimit("256")).resolves.toBe(256);
  });

  it.each(["49", "513", "not-a-number"])(
    "rejects unsafe value %s",
    async value => {
      await expect(loadLimit(value)).rejects.toThrow();
    },
  );
});
