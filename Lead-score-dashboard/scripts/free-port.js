/**
 * Frees a TCP port on Windows before starting Vite (avoids 5173 vs 5174 confusion).
 * Usage: node scripts/free-port.js 5173
 */
import { execSync } from "node:child_process";

const port = process.argv[2] || "5173";

try {
  const out = execSync(
    `powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"`,
    { encoding: "utf8" }
  ).trim();

  if (!out) {
    console.log(`Port ${port} is free.`);
    process.exit(0);
  }

  const pids = [...new Set(out.split(/\s+/).filter(Boolean))];
  for (const pid of pids) {
    try {
      execSync(`taskkill /PID ${pid} /F`, { stdio: "ignore" });
      console.log(`Stopped process ${pid} on port ${port}`);
    } catch {
      /* already gone */
    }
  }
} catch {
  console.log(`Port ${port} is free.`);
}
