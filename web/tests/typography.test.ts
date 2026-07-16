import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf8");
const requiredStack = 'Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

function declarationValues(property: string) {
  const pattern = new RegExp(`\\b${property}\\s*:\\s*([^;}]+)`, "g");
  return [...css.matchAll(pattern)].map((match) => match[1].trim());
}

describe("portal typography", () => {
  it("uses one accessible sans-serif stack", () => {
    const families = declarationValues("font-family");

    expect(families).toContain(requiredStack);
    expect(families.every((value) => value === requiredStack || value === "inherit")).toBe(true);
    expect(css).not.toMatch(/(?:^|[\s,:])(?:serif|monospace)(?=[\s,;}])/im);
  });

  it("uses no font shorthand except inheritance", () => {
    expect(declarationValues("font").every((value) => value === "inherit")).toBe(true);
  });

  it("never sets a font-size pixel token below 14px", () => {
    const declarations = declarationValues("font-size");

    expect(declarations.length).toBeGreaterThan(0);
    for (const declaration of declarations) {
      if (declaration === "inherit") continue;

      const pixelSizes = [...declaration.matchAll(/(-?\d+(?:\.\d+)?)px/g)].map(
        (match) => Number(match[1]),
      );
      expect(pixelSizes.length, `font-size must use px tokens: ${declaration}`).toBeGreaterThan(0);
      expect(pixelSizes.filter((size) => size < 14), declaration).toEqual([]);
    }
  });

  it("sets the body copy to 16px", () => {
    expect(css).toMatch(/body\s*\{[^}]*font-size:\s*16px/s);
  });

  it("neutralizes native small and code typography", () => {
    expect(css).toMatch(/(?:^|})\s*small\s*\{[^}]*font-size:\s*inherit\s*;/s);
    expect(css).toMatch(/(?:^|})\s*code\s*\{[^}]*font-family:\s*inherit\s*;[^}]*font-size:\s*inherit\s*;/s);
  });
});
