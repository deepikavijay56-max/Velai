"use client";

import { FormEvent, useCallback, useState } from "react";

const API_V1 = `${(process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "")}/api/v1`;

interface AdminStats {
  total_users: number;
  total_gigs: number;
  total_contracts: number;
  flagged_academic_gigs: number;
  pending_org_verifications: number;
}

interface Organization {
  id: string;
  name: string;
  type: string;
  owner_id: string;
  verified_status: string;
}

interface FlaggedGig {
  id: string;
  title: string;
  flag_reason: string | null;
  status: string;
  poster: { name: string; college_email: string } | null;
}

interface OtpResponse {
  dev_mock_otp: string | null;
}

interface AuthResponse {
  access_token: string;
  user: { name: string; role: string };
}

async function apiRequest<T>(
  path: string,
  accessToken?: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init?.headers,
    },
  });
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      body && typeof body === "object" && "detail" in body && typeof body.detail === "string"
        ? body.detail
        : undefined;
    throw new Error(detail ?? `Backend request failed (${response.status}).`);
  }
  if (body === null) throw new Error("The backend returned an empty response.");
  return body as T;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unexpected backend error.";
}

export default function Home() {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [loginMessage, setLoginMessage] = useState("");
  const [loginError, setLoginError] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [flaggedGigs, setFlaggedGigs] = useState<FlaggedGig[]>([]);
  const [dashboardError, setDashboardError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRequestingOtp, setIsRequestingOtp] = useState(false);
  const [isVerifyingOtp, setIsVerifyingOtp] = useState(false);
  const [busyAction, setBusyAction] = useState("");

  const loadDashboard = useCallback(async (token: string) => {
    setIsLoading(true);
    setDashboardError("");
    try {
      const [nextStats, nextOrganizations, nextFlaggedGigs] = await Promise.all([
        apiRequest<AdminStats>("/admin/stats", token),
        apiRequest<Organization[]>("/admin/orgs?status_filter=pending", token),
        apiRequest<FlaggedGig[]>("/admin/moderation", token),
      ]);
      setStats(nextStats);
      setOrganizations(nextOrganizations);
      setFlaggedGigs(nextFlaggedGigs);
    } catch (error) {
      setDashboardError(errorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, []);

  async function requestOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsRequestingOtp(true);
    setLoginError("");
    setLoginMessage("");
    setDevOtp(null);
    try {
      const response = await apiRequest<OtpResponse>("/auth/request-otp", undefined, {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      });
      setDevOtp(response.dev_mock_otp);
      setLoginMessage(
        response.dev_mock_otp
          ? "Development OTP received. Use the code shown below."
          : "OTP requested. Check your college email.",
      );
    } catch (error) {
      setLoginError(errorMessage(error));
    } finally {
      setIsRequestingOtp(false);
    }
  }

  async function verifyOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsVerifyingOtp(true);
    setLoginError("");
    try {
      const response = await apiRequest<AuthResponse>("/auth/verify-otp", undefined, {
        method: "POST",
        body: JSON.stringify({ email: email.trim().toLowerCase(), otp_code: otp.trim() }),
      });
      if (response.user.role !== "admin") {
        throw new Error("This account does not have administrator access.");
      }
      setAccessToken(response.access_token);
      await loadDashboard(response.access_token);
    } catch (error) {
      setLoginError(errorMessage(error));
    } finally {
      setIsVerifyingOtp(false);
    }
  }

  function signOut() {
    setAccessToken("");
    setStats(null);
    setOrganizations([]);
    setFlaggedGigs([]);
    setDashboardError("");
  }

  async function reviewOrganization(id: string, action: "approve" | "reject") {
    setBusyAction(id);
    setDashboardError("");
    try {
      await apiRequest<Organization>(`/admin/orgs/${id}/${action}`, accessToken, {
        method: "POST",
      });
      await loadDashboard(accessToken);
    } catch (error) {
      setDashboardError(errorMessage(error));
    } finally {
      setBusyAction("");
    }
  }

  async function resolveFlaggedGig(id: string, action: "approve" | "cancel") {
    setBusyAction(id);
    setDashboardError("");
    try {
      await apiRequest<FlaggedGig>(
        `/admin/moderation/${id}/resolve?action=${action}`,
        accessToken,
        { method: "POST" },
      );
      await loadDashboard(accessToken);
    } catch (error) {
      setDashboardError(errorMessage(error));
    } finally {
      setBusyAction("");
    }
  }

  if (!accessToken) {
    return (
      <main className="page-shell login-shell">
        <section className="panel login-panel">
          <p className="eyebrow">Velai admin</p>
          <h1>Administrator sign in</h1>
          <p className="login-help">
            Sign in with the administrator college email configured for the backend.
          </p>
          <form className="admin-form" onSubmit={requestOtp}>
            <label htmlFor="admin-email">College email</label>
            <input
              id="admin-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            <button className="primary-btn" type="submit" disabled={isRequestingOtp}>
              {isRequestingOtp ? "Requesting…" : "Request OTP"}
            </button>
          </form>
          {loginMessage && <p className="success-message">{loginMessage}</p>}
          {devOtp && <p className="dev-otp">Development OTP: {devOtp}</p>}
          {loginMessage && (
            <form className="admin-form" onSubmit={verifyOtp}>
              <label htmlFor="admin-otp">Verification code</label>
              <input
                id="admin-otp"
                inputMode="numeric"
                autoComplete="one-time-code"
                value={otp}
                onChange={(event) => setOtp(event.target.value)}
                required
              />
              <button className="primary-btn" type="submit" disabled={isVerifyingOtp}>
                {isVerifyingOtp ? "Signing in…" : "Sign in"}
              </button>
            </form>
          )}
          {loginError && <p className="error-message">{loginError}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Velai admin</p>
          <h1>Moderation dashboard</h1>
        </div>
        <div className="header-actions">
          <button
            className="ghost-btn"
            onClick={() => void loadDashboard(accessToken)}
            disabled={isLoading}
          >
            {isLoading ? "Refreshing…" : "Refresh"}
          </button>
          <button className="primary-btn" onClick={signOut}>Sign out</button>
        </div>
      </header>

      {dashboardError && <p className="error-message" role="alert">{dashboardError}</p>}

      <section className="stats-grid">
        {[
          ["Users", stats?.total_users],
          ["Gigs", stats?.total_gigs],
          ["Contracts", stats?.total_contracts],
          ["Pending org approvals", stats?.pending_org_verifications],
          ["Flagged gigs", stats?.flagged_academic_gigs],
        ].map(([label, value]) => (
          <article className="stat-card" key={label}>
            <span className="stat-label">{label}</span>
            <strong>{value ?? (isLoading ? "…" : "—")}</strong>
            <small>Live backend count</small>
          </article>
        ))}
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-header">
            <h2>Organisation approvals</h2>
            <span className="pill neutral">{organizations.length} pending</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Name</th><th>Type</th><th>Owner ID</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {organizations.map((organization) => (
                  <tr key={organization.id}>
                    <td>{organization.name}</td>
                    <td>{organization.type}</td>
                    <td>{organization.owner_id}</td>
                    <td className="actions-cell">
                      <button
                        className="ghost-btn"
                        disabled={busyAction === organization.id}
                        onClick={() => void reviewOrganization(organization.id, "approve")}
                      >
                        Approve
                      </button>
                      <button
                        className="danger-btn"
                        disabled={busyAction === organization.id}
                        onClick={() => void reviewOrganization(organization.id, "reject")}
                      >
                        Reject
                      </button>
                    </td>
                  </tr>
                ))}
                {!organizations.length && (
                  <tr><td colSpan={4}>{isLoading ? "Loading…" : "No pending organizations."}</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>Flagged gigs</h2>
            <span className="pill danger">{flaggedGigs.length} flagged</span>
          </div>
          <ul className="list-stack">
            {flaggedGigs.map((gig) => (
              <li key={gig.id} className="list-item">
                <div className="flagged-copy">
                  <strong>{gig.title}</strong>
                  <small>{gig.flag_reason ?? "Flagged for review"}</small>
                  <small>{gig.poster?.name ?? gig.poster?.college_email ?? "Unknown poster"}</small>
                </div>
                <div className="flagged-actions">
                  <button
                    className="ghost-btn"
                    disabled={busyAction === gig.id}
                    onClick={() => void resolveFlaggedGig(gig.id, "approve")}
                  >
                    Clear flag
                  </button>
                  <button
                    className="danger-btn"
                    disabled={busyAction === gig.id}
                    onClick={() => void resolveFlaggedGig(gig.id, "cancel")}
                  >
                    Cancel gig
                  </button>
                </div>
              </li>
            ))}
            {!flaggedGigs.length && (
              <li className="list-item">
                <small>{isLoading ? "Loading…" : "No gigs are currently flagged."}</small>
              </li>
            )}
          </ul>
        </div>
      </section>
    </main>
  );
}
