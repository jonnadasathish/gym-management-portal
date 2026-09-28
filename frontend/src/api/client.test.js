import { afterEach, describe, expect, it } from "vitest";

import { clearAccessToken, setAccessToken } from "./client";

describe("access token memory slot", () => {
  afterEach(() => {
    clearAccessToken();
  });

  it("stores the access token on window, never localStorage", () => {
    setAccessToken("test-access");
    expect(window.__gymportalAccessToken).toBe("test-access");
    expect(window.localStorage.getItem("access")).toBeNull();
    expect(window.sessionStorage.getItem("access")).toBeNull();
    clearAccessToken();
    expect(window.__gymportalAccessToken).toBeNull();
  });
});
