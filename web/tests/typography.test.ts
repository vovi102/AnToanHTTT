import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf8");

describe("portal typography", () => {
  it("uses one accessible sans-serif stack", () => {
    expect(css).toContain('Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif');
    expect(css).not.toMatch(/Georgia|Times New Roman/);
    expect(css).not.toMatch(/font-size:\s*0(?:px)?\s*;/);
  });

  it("never sets pixel font sizes below 14px", () => {
    const sizes = [...css.matchAll(/font-size:\s*(\d+(?:\.\d+)?)px/g)].map(
      (match) => Number(match[1]),
    );
    expect(sizes.length).toBeGreaterThan(0);
    expect(sizes.filter((size) => size < 14)).toEqual([]);
  });

  it("sets the body copy to 16px", () => {
    expect(css).toMatch(/body\s*\{[^}]*font-size:\s*16px/s);
  });
});
