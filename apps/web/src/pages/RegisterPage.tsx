import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
} from "../components/ui";
import { getApiPrefix } from "../lib/api";
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

export function RegisterPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [orgName, setOrgName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await fetch(`${getApiPrefix()}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          organization_name: orgName,
        }),
      });
      if (!r.ok) {
        const j = (await r.json().catch(() => ({}))) as { message?: string };
        setErr(j.message ?? `HTTP ${r.status}`);
        return;
      }
      const j = (await r.json()) as {
        access_token: string;
        refresh_token: string;
      };
      localStorage.setItem("frodo_access_token", j.access_token);
      localStorage.setItem("frodo_refresh_token", j.refresh_token);
      persistProfile(fullName, email);
      nav("/workspace");
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="rounded-2xl border border-zinc-800 bg-zinc-900/80 p-8 shadow-2xl backdrop-blur-xl"
    >
      <motion.div variants={itemVariants} className="text-center">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Frodo
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          One platform to rule them all
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="mt-6">
        <Card className="border-zinc-800 bg-transparent shadow-none">
          <CardHeader className="border-none px-0 pb-2 pt-0 text-center">
            <CardTitle className="text-xl text-white">Create account</CardTitle>
            <CardDescription>
              Password must be 8+ characters with upper, lower, and digit (API
              rule).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 px-0">
            <AnimatePresence mode="wait">
              {err && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="rounded-lg border border-red-800/60 bg-red-950/50 px-4 py-3 text-sm text-red-300"
                  role="alert"
                >
                  {err}
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={(e) => void submit(e)} className="space-y-4">
              <motion.div variants={itemVariants}>
                <Input
                  label="Full name"
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </motion.div>
              <motion.div variants={itemVariants}>
                <Input
                  label="Organization"
                  autoComplete="organization"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  required
                />
              </motion.div>
              <motion.div variants={itemVariants}>
                <Input
                  label="Email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </motion.div>
              <motion.div variants={itemVariants}>
                <Input
                  label="Password"
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </motion.div>
              <motion.div variants={itemVariants}>
                <Button
                  type="submit"
                  variant="gradient"
                  className="w-full"
                  disabled={loading}
                >
                  {loading ? "Creating account…" : "Create account"}
                </Button>
              </motion.div>
            </form>

            <p className="mt-4 text-center text-sm text-zinc-500">
              Already registered?{" "}
              <Link
                to="/login"
                className="font-medium text-coral transition-colors hover:text-coral-dark"
              >
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
