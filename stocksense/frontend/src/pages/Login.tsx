import { type FormEvent, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { ArrowRight, KeyRound, LockKeyhole, Package, ShieldCheck, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { apiPost, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { AuthResponse } from "@/lib/types";

type Mode = "login" | "signup" | "otp" | "forgot" | "reset";

function errorMessage(error: unknown) {
  if (error instanceof ApiError && typeof error.body === "object" && error.body && "detail" in error.body) return String((error.body as { detail: string }).detail);
  return "Something went wrong. Please try again.";
}

export default function Login() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [busyError, setBusyError] = useState("");

  const auth = useMutation({
    mutationFn: async () => {
      if (mode === "signup") return apiPost<AuthResponse>("/auth/signup", { email, password, name });
      if (mode === "otp") return apiPost<AuthResponse>("/auth/verify-otp", { email, code });
      if (mode === "forgot") return apiPost<{ message: string; demo_code: string }>("/auth/forgot-password", { email });
      if (mode === "reset") return apiPost<{ message: string }>("/auth/reset-password", { email, code, password });
      return apiPost<AuthResponse>("/auth/login", { email, password });
    },
    onSuccess: (result) => {
      setBusyError("");
      if (mode === "signup") {
        setMode("otp");
        toast.success("Verification code ready", { description: "Use 123456 for this demo workspace." });
        return;
      }
      if (mode === "otp") {
        queryClient.setQueryData(["me"], (result as AuthResponse).user);
        navigate("/app");
        return;
      }
      if (mode === "forgot") {
        setMode("reset");
        toast.success("Reset code ready", { description: "Use 123456 for this demo workspace." });
        return;
      }
      if (mode === "reset") {
        setMode("login");
        toast.success("Password updated");
        return;
      }
      queryClient.setQueryData(["me"], (result as AuthResponse).user);
      navigate("/app");
    },
    onError: (error) => setBusyError(errorMessage(error)),
  });

  const submit = (event: FormEvent) => { event.preventDefault(); auth.mutate(); };
  const demoLogin = (role: "manager" | "staff") => {
    const demoEmail = role === "manager" ? "manager@stocksense.demo" : "staff@stocksense.demo";
    setEmail(demoEmail);
    setPassword("StockSense123!");
    setMode("login");
    setBusyError("");
    apiPost<AuthResponse>("/auth/login", { email: demoEmail, password: "StockSense123!" }).then((result) => {
      queryClient.setQueryData(["me"], result.user);
      navigate("/app");
    }).catch((error: unknown) => setBusyError(errorMessage(error)));
  };

  const title = mode === "login" ? "Sign in to your workspace" : mode === "signup" ? "Create your operator profile" : mode === "otp" ? "Verify your account" : mode === "forgot" ? "Recover access" : "Set a new password";
  const description = mode === "login" ? "Your live operating picture, one calm decision at a time." : mode === "otp" ? "Enter the six-digit code sent to your inbox." : "StockSense keeps every movement accountable.";

  return (
    <main className="min-h-svh overflow-hidden bg-[#090d14] text-slate-100">
      <div className="grid min-h-svh lg:grid-cols-[1.08fr_0.92fr]">
        <section className="relative hidden overflow-hidden border-r border-white/10 bg-[#101722] p-10 lg:flex lg:flex-col lg:justify-between xl:p-16">
          <div className="absolute -right-24 top-20 h-96 w-96 rounded-full bg-amber-400/10 blur-3xl" />
          <div className="relative">
            <div className="flex items-center gap-3" data-testid="auth-brand-mark"><div className="grid h-10 w-10 place-items-center rounded-xl bg-amber-400 text-slate-950 shadow-[0_0_32px_rgba(245,158,11,0.28)]"><Package size={21} strokeWidth={2.5} /></div><span className="text-xl font-semibold tracking-tight">StockSense</span></div>
            <div className="mt-28 max-w-xl">
              <p className="mb-5 font-mono text-xs uppercase tracking-[0.24em] text-amber-300">Inventory operations / 06:42 UTC</p>
              <h1 className="text-5xl font-semibold leading-[1.03] tracking-[-0.04em] text-white xl:text-7xl">The warehouse,<br /><span className="text-amber-300">in focus.</span></h1>
              <p className="mt-7 max-w-md text-base leading-7 text-slate-400">A precise command center for keeping product, people, and movement in sync across every location.</p>
            </div>
          </div>
          <div className="relative grid max-w-xl grid-cols-3 gap-3" data-testid="auth-preview-metrics">
            {[['01', 'Single source of truth'], ['02', 'Ledger-grade history'], ['03', 'Decisions at a glance']].map(([number, label]) => <div className="border-l border-amber-400/40 pl-4" key={number}><div className="font-mono text-xs text-amber-300">{number}</div><div className="mt-2 text-sm text-slate-400">{label}</div></div>)}
          </div>
        </section>
        <section className="flex items-center justify-center p-6 sm:p-12">
          <div className="w-full max-w-md">
            <div className="mb-12 flex items-center gap-3 lg:hidden"><div className="grid h-10 w-10 place-items-center rounded-xl bg-amber-400 text-slate-950"><Package size={21} /></div><span className="text-xl font-semibold">StockSense</span></div>
            <div className="mb-8"><div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-amber-400/20 bg-amber-400/10 text-amber-300"><LockKeyhole size={21} /></div><h2 className="text-3xl font-semibold tracking-tight text-white" data-testid="auth-page-title">{title}</h2><p className="mt-2 text-sm leading-6 text-slate-400">{description}</p></div>
            <form onSubmit={submit} className="space-y-4" data-testid="auth-form">
              {mode === "signup" && <Input data-testid="signup-name-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" required />}
              <Input data-testid="login-email-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@company.com" required />
              {(mode === "login" || mode === "signup" || mode === "reset") && <Input data-testid="login-password-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={mode === "reset" ? "New password" : "Password"} required />}
              {(mode === "otp" || mode === "reset") && <Input data-testid="otp-input" inputMode="numeric" value={code} onChange={(e) => setCode(e.target.value)} placeholder="6-digit code · demo: 123456" required />}
              {busyError && <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-200" data-testid="auth-error-message">{busyError}</div>}
              <Button data-testid="login-submit-button" disabled={auth.isPending} className="h-12 w-full justify-between rounded-xl bg-amber-400 px-5 font-semibold text-slate-950 hover:bg-amber-300">{auth.isPending ? "Working…" : mode === "login" ? "Enter workspace" : mode === "signup" ? "Create account" : mode === "otp" ? "Verify and continue" : mode === "forgot" ? "Send reset code" : "Update password"}<ArrowRight size={17} /></Button>
            </form>
            {mode === "login" && <div className="mt-7 space-y-3"><div className="flex items-center gap-3 text-[11px] uppercase tracking-widest text-slate-500"><span className="h-px flex-1 bg-white/10" />Demo access<span className="h-px flex-1 bg-white/10" /></div><div className="grid grid-cols-2 gap-3"><Button data-testid="demo-login-manager-button" type="button" variant="outline" className="h-auto justify-start rounded-xl border-white/10 bg-white/[0.03] px-4 py-3 text-left hover:bg-white/[0.08]" onClick={() => demoLogin("manager")}><Sparkles size={15} className="mr-2 text-amber-300" /><span><b className="block text-xs text-white">Manager</b><small className="text-[10px] text-slate-500">Full controls</small></span></Button><Button data-testid="demo-login-staff-button" type="button" variant="outline" className="h-auto justify-start rounded-xl border-white/10 bg-white/[0.03] px-4 py-3 text-left hover:bg-white/[0.08]" onClick={() => demoLogin("staff")}><ShieldCheck size={15} className="mr-2 text-emerald-300" /><span><b className="block text-xs text-white">Warehouse staff</b><small className="text-[10px] text-slate-500">Floor view</small></span></Button></div></div>}
            <div className="mt-8 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-500">{mode === "login" ? <><button data-testid="forgot-password-link" type="button" className="hover:text-amber-300" onClick={() => { setMode("forgot"); setBusyError(""); }}>Forgot password?</button><button data-testid="signup-link" type="button" className="text-slate-300 hover:text-amber-300" onClick={() => { setMode("signup"); setBusyError(""); }}>Create an account <ArrowRight className="ml-1 inline" size={14} /></button></> : <button data-testid="back-to-login-link" type="button" className="hover:text-amber-300" onClick={() => { setMode("login"); setBusyError(""); }}><KeyRound className="mr-1 inline" size={14} />Back to sign in</button>}</div>
            <p className="mt-12 text-center text-xs leading-5 text-slate-600">Demo credentials use realistic seeded workspace data.<br />Manager and staff views share one operational ledger.</p>
          </div>
        </section>
      </div>
    </main>
  );
}