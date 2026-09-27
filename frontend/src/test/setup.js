import "@testing-library/jest-dom/vitest";

// The auth module relies on localStorage. Node's test environment
// does not provide it, so we install a minimal in-memory shim.
if (!globalThis.localStorage) {
  const store = new Map();

  globalThis.localStorage = {
    getItem: (key) => (store.has(key) ? store.get(key) : null),
    setItem: (key, value) => store.set(key, String(value)),
    removeItem: (key) => store.delete(key),
    clear: () => store.clear(),
  };
}