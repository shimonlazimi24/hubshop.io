import { AnimatePresence, motion } from "framer-motion";
import { Check } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent } from "../components/ui";
import {
  API_DOWN_HINT,
  errorMessageFromFailedResponse,
  getApiPrefix,
} from "../lib/api";
import { persistProfile } from "../lib/user-profile";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] as const },
  },
};

export function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await fetch(`${getApiPrefix()}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!r.ok) {
        setErr(await errorMessageFromFailedResponse(r));
        return;
      }
      const j = (await r.json()) as {
        access_token: string;
        refresh_token: string;
      };
      localStorage.setItem("frodo_access_token", j.access_token);
      localStorage.setItem("frodo_refresh_token", j.refresh_token);
      const friendly =
        email.includes("@") && email.split("@")[0]
          ? email.split("@")[0]!
          : "User";
      persistProfile(friendly, email);
      setSuccess(true);
      setTimeout(() => nav("/workspace"), 600);
    } catch (e) {
      setErr(
        e instanceof TypeError
          ? API_DOWN_HINT
          : e instanceof Error
            ? e.message
            : "Request failed",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="flex h-16 w-16 items-center justify-center rounded-full border border-success/30 bg-success/20"
            >
              <Check className="h-8 w-8 text-success" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="rounded-2xl border border-zinc-800 bg-zinc-900/80 p-8 shadow-2xl backdrop-blur-xl"
      >
        <motion.div variants={itemVariants} className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Hubshop
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            One platform to rule them all
          </p>
        </motion.div>

        <motion.div variants={itemVariants} className="mt-6">
          <Card className="border-zinc-800 bg-transparent shadow-none">
            <CardContent className="space-y-4 px-0 pt-0">
              <AnimatePresence mode="wait">
                {err && (
                  <motion.div
                    initial={{ opacity: 0, x: 0 }}
                    animate={{
                      opacity: 1,
                      x: [0, -8, 8, -6, 6, -3, 3, 0],
                    }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.4 }}
                    className="rounded-lg border border-red-800/60 bg-red-950/50 px-4 py-3 text-sm text-red-300"
                    role="alert"
                  >
                    {err}
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={(e) => void submit(e)} className="space-y-4">
                <motion.div variants={itemVariants}>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-zinc-300"
                  >
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 transition-shadow focus:border-coral/50 focus:outline-none focus:ring-2 focus:ring-coral/20"
                  />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-zinc-300"
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-500 transition-shadow focus:border-coral/50 focus:outline-none focus:ring-2 focus:ring-coral/20"
                  />
                </motion.div>
                <motion.div variants={itemVariants}>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full rounded-lg bg-coral px-4 py-3 font-medium text-white transition-colors hover:bg-coral-dark disabled:opacity-50"
                  >
                    {loading ? "Signing in…" : "Sign in with email"}
                  </button>
                </motion.div>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        <motion.p
          variants={itemVariants}
          className="mt-6 text-center text-sm text-zinc-500"
        >
          Don&apos;t have an account?{" "}
          <Link
            to="/register"
            className="text-coral transition-colors hover:text-coral-dark"
          >
            Create account
          </Link>
        </motion.p>
      </motion.div>
    </>
  );
}
