import { beforeEach, describe, expect, it } from "vitest";

import { tokenStorage } from "../tokenStorage";

describe("tokenStorage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("returns null for access/refresh when nothing is stored", () => {
    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });

  it("setTokens stores both access and refresh tokens", () => {
    tokenStorage.setTokens("access-123", "refresh-456");
    expect(tokenStorage.getAccess()).toBe("access-123");
    expect(tokenStorage.getRefresh()).toBe("refresh-456");
  });

  it("setAccess updates only the access token", () => {
    tokenStorage.setTokens("access-123", "refresh-456");
    tokenStorage.setAccess("new-access");
    expect(tokenStorage.getAccess()).toBe("new-access");
    expect(tokenStorage.getRefresh()).toBe("refresh-456");
  });

  it("clear removes both tokens", () => {
    tokenStorage.setTokens("access-123", "refresh-456");
    tokenStorage.clear();
    expect(tokenStorage.getAccess()).toBeNull();
    expect(tokenStorage.getRefresh()).toBeNull();
  });
});
