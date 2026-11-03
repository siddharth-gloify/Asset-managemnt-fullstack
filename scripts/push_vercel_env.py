"""Push every variable in .env.vercel to the linked Vercel project (Production).

    vercel login && vercel link        # once
    python scripts/push_vercel_env.py

Values are piped to `vercel env add` over stdin, so they never appear in the process list.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env.vercel"
TARGETS = ["production"]


def main() -> int:
    vercel = shutil.which("vercel") or shutil.which("vercel.cmd")
    if not vercel:
        print("Vercel CLI not found. Install it with: npm i -g vercel")
        return 1
    if not (ROOT / ".vercel" / "project.json").exists():
        print("Project is not linked. Run: vercel link")
        return 1
    if not ENV_FILE.exists():
        print("Missing .env.vercel. Run: python scripts/make_vercel_env.py --allowed-ips <CIDRs>")
        return 1

    failed = 0
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        for target in TARGETS:
            # `--force` overwrites an existing variable of the same name.
            result = subprocess.run(
                [vercel, "env", "add", key, target, "--force"],
                input=value + "\n",
                text=True,
                capture_output=True,
                cwd=ROOT,
            )
            status = "ok" if result.returncode == 0 else "FAILED"
            if result.returncode:
                failed += 1
                print(result.stderr.strip()[:300])
            print(f"{status:7} {key} -> {target}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
