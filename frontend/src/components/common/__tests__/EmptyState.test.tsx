import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EmptyState } from "../EmptyState";

describe("EmptyState", () => {
  it("renders the title", () => {
    render(<EmptyState title="No entries yet" />);
    expect(screen.getByText("No entries yet")).toBeInTheDocument();
  });

  it("renders the description when provided", () => {
    render(<EmptyState title="No entries yet" description="Start by logging your first mood." />);
    expect(screen.getByText("Start by logging your first mood.")).toBeInTheDocument();
  });

  it("omits the description when not provided", () => {
    render(<EmptyState title="No entries yet" />);
    expect(screen.queryByText(/start by/i)).not.toBeInTheDocument();
  });

  it("renders the action element when provided", () => {
    render(<EmptyState title="No entries yet" action={<button>Add one</button>} />);
    expect(screen.getByRole("button", { name: "Add one" })).toBeInTheDocument();
  });
});
