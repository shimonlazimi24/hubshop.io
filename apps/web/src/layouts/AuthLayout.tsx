import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-zinc-950 px-4 py-12">
      <div className="auth-mesh-bg" aria-hidden />
      <div className="relative z-10 w-full max-w-md space-y-6">
        <Outlet />
      </div>
    </div>
  );
}
