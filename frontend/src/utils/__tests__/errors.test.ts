import { AxiosError } from "axios";
import { describe, expect, it } from "vitest";

import { extractErrorMessage } from "../errors";

function makeAxiosError(data: unknown, message = "Request failed") {
  const error = new AxiosError(message);
  error.response = {
    data,
    status: 400,
    statusText: "Bad Request",
    headers: {},
    config: {} as never,
  };
  return error;
}

describe("extractErrorMessage", () => {
  it("extracts the message from the backend's standard error envelope", () => {
    const error = makeAxiosError({ success: false, error: { code: "ValidationError", message: "Email is invalid.", details: null } });
    expect(extractErrorMessage(error)).toBe("Email is invalid.");
  });

  it("falls back to the axios error message when the envelope is missing", () => {
    const error = makeAxiosError({ unexpected: "shape" }, "Network Error");
    expect(extractErrorMessage(error)).toBe("Network Error");
  });

  it("handles plain Error instances", () => {
    expect(extractErrorMessage(new Error("Something broke"))).toBe("Something broke");
  });

  it("returns the fallback for unrecognized error shapes", () => {
    expect(extractErrorMessage("a plain string", "Default message")).toBe("Default message");
  });

  it("uses the default fallback when none is provided", () => {
    expect(extractErrorMessage(null)).toBe("Something went wrong.");
  });
});
