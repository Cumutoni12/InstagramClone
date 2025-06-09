import { expect, afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
// Cleanup after each test to remove rendered components
import * as matchers from "@testing-library/jest-dom/matchers";

//extend vistest expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();

  vi.clearAllMocks(); // Clear all mocks after each test

  // restore original fetch funtionality if you mocked it globally

  if (global.fetch.mockRestore) {
    global.fetch.mockRestore();
  }
});

// Mock the intersecting observer Api often used by librariesF

const mockIntersectionObserver = vi.fn();

mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null,
});
Object.defineProperty(window, "IntersectionObserver", {
  writable: true,
  value: mockIntersectionObserver,
});
