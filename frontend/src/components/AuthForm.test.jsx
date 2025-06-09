import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import AuthForm from "./AuthForm";

//mock the useAuth hook for testing authForm in isolation

import { useAuth } from "../context/AuthContext";

// Mock the useAuth hook

vi.mock("../context/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    user: null, // simulate not authenticated initially
    iseAuthenticated: false,
    loading: false,
    login: vi.fn(), // mock the login function
    logout: vi.fn(),
  })),
}));

describe("AuthForm Component", () => {
  it("renders login form correctly", () => {
    render(<AuthForm type="login" />);

    expect(screen.getByPlaceholderText("Username")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /sign up/i })
    ).not.toBeInTheDocument(); // check signup button is not there
  });

  it("renders signup form correctly", () => {
    render(<AuthForm type="signup" />);

    expect(
      screen.getByRole("button", { name: /sign up/i })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /log in/i })
    ).not.toBeInTheDocument(); // Check login button is NOT there
  });

  it("shows error message for empty fields on submit", async () => {
    render(<AuthForm type="login" />);

    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Please enter both username and password")
      ).toBeInTheDocument();
    });
  });

  it("calls fetch and login on successful login submit", async () => {
    const mockLogin = vi.fn();
    useAuth.mockReturnValue({
      // Override mock return value for this test
      user: null,
      isAuthenticated: false,
      loading: false,
      login: mockLogin,
      logout: vi.fn(),
    });

    // Mock the global fetch function
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            message: "Login successful",
            username: "testuser",
            token: "fake-token",
          }),
      })
    );

    render(<AuthForm type="login" />);

    fireEvent.change(screen.getByPlaceholderText("Username"), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    // Wait for the async fetch and state updates
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:5000/login", // Check API URL
        expect.objectContaining({
          // Check request options
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: "testuser",
            password: "password123",
          }),
        })
      );
      expect(mockLogin).toHaveBeenCalledWith({
        username: "testuser",
        token: "fake-token",
      }); // Check if login context function was called
    });

    expect(
      screen.queryByText("Please enter both username and password")
    ).not.toBeInTheDocument(); // Ensure validation error is gone
  });

  // Add tests for signup similarly
  it("calls fetch and login on successful signup submit", async () => {
    const mockLogin = vi.fn();
    useAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      loading: false,
      login: mockLogin,
      logout: vi.fn(),
    });

    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            message: "User created successfully",
            username: "newuser",
            token: "fake-new-token",
          }),
      })
    );

    render(<AuthForm type="signup" />);

    fireEvent.change(screen.getByPlaceholderText("Username"), {
      target: { value: "newuser" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "newpassword123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:5000/signup",
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: "newuser",
            password: "newpassword123",
          }),
        })
      );
      expect(mockLogin).toHaveBeenCalledWith({
        username: "newuser",
        token: "fake-new-token",
      });
    });
  });

  // Add tests for API error handling
  it("shows error message on API login failure", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false, // Simulate API error
        status: 401,
        json: () => Promise.resolve({ message: "Invalid credentials" }),
      })
    );

    render(<AuthForm type="login" />);

    fireEvent.change(screen.getByPlaceholderText("Username"), {
      target: { value: "wronguser" },
    });
    fireEvent.change(screen.getByPlaceholderText("Password"), {
      target: { value: "wrongpassword" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(screen.getByText("Invalid credentials")).toBeInTheDocument(); // Show error message from API
    });
    // Ensure login was NOT called
    expect(useAuth().login).not.toHaveBeenCalled();
  });
});
