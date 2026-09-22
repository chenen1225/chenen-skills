/**
 * TypeSafe multi-key rotating client — reference implementation.
 *
 * Drop-in HTTP client for `POST https://api.typesafe.ai/v1/systemone`.
 * The official TypeSafe SDKs read only a single `TYPESAFE_API_KEY` and have no
 * built-in key rotation, so this uses the raw HTTP API to add:
 *   - a self-managed key pool (TYPESAFE_API_KEYS="k1,k2,k3" or TYPESAFE_API_KEY)
 *   - rotation on 401 Unauthorized (bad key is marked dead, next key is tried)
 *   - exponential backoff on 429 Too Many Requests / 529 Overloaded
 *   - zero key storage: keys live in your env / .env, never in this file
 *   - best-effort .env auto-load: if the consuming project has `dotenv`
 *     installed, this file loads `.env` from the project cwd automatically,
 *     so you can just drop TYPESAFE_API_KEYS into `.env` with no manual loader
 *
 * Requires Node 20+ (global fetch) and, for .env support, `dotenv`
 * (`npm i dotenv`) in the consuming project. Adjust to your stack as needed.
 */

// Best-effort: load `.env` from the consuming project's cwd so that
// TYPESAFE_API_KEYS / TYPESAFE_API_KEY work without a manual loader.
// No-op (and no error) if `dotenv` isn't installed — real env vars still work.
import("dotenv/config").catch(() => {});

export interface TypeSafeAnswer {
  type: "noul" | "choice" | "score";
  // noul
  noul?: number;
  // choice
  choice?: string;
  probabilities?: Record<string, number>;
  confidence?: number;
  // score
  score?: number;
  legend?: Record<string, string>;
}

export interface TypeSafeResponse {
  model: string;
  answers: Record<string, TypeSafeAnswer>;
  usage: { input_tokens: number; output_tokens: number };
}

export interface TypeSafeRequest {
  state: unknown;
  model?: string;
  questions: Record<string, unknown>;
}

const ENDPOINT = "https://api.typesafe.ai/v1/systemone";
const MODEL = "jev-latest";

function loadKeys(): string[] {
  const raw =
    process.env.TYPESAFE_API_KEYS ?? process.env.TYPESAFE_API_KEY ?? "";
  const keys = raw
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);
  if (keys.length === 0) {
    throw new Error(
      "No TypeSafe key found. Set TYPESAFE_API_KEYS (comma-separated) or TYPESAFE_API_KEY."
    );
  }
  return keys;
}

export class TypeSafeRotatingClient {
  private keys: string[];
  private dead = new Set<number>();
  private cursor = 0;

  constructor(private endpoint = ENDPOINT, private model = MODEL) {
    this.keys = loadKeys();
  }

  /** Pick the next live key, round-robin. Throws if every key is dead. */
  private nextKeyIndex(): number {
    for (let i = 0; i < this.keys.length; i++) {
      this.cursor = (this.cursor + 1) % this.keys.length;
      if (!this.dead.has(this.cursor)) return this.cursor;
    }
    throw new Error("All TypeSafe API keys are dead (401). Check your keys.");
  }

  async systemOne(
    state: unknown,
    questions: Record<string, unknown>,
    options: { maxBackoff?: number; maxAttempts?: number } = {}
  ): Promise<TypeSafeResponse> {
    const maxBackoff = options.maxBackoff ?? 30000;
    const maxAttempts = options.maxAttempts ?? this.keys.length * 4;
    let attempt = 0;

    while (attempt < maxAttempts) {
      const idx = this.nextKeyIndex();
      const res = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.keys[idx]}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ state, model: this.model, questions }),
      });

      if (res.status === 401) {
        this.dead.add(idx); // invalid key, drop it and rotate
        continue;
      }
      if (res.status === 429 || res.status === 529) {
        const wait = Math.min(1000 * 2 ** attempt, maxBackoff);
        await new Promise((r) => setTimeout(r, wait));
        attempt++;
        continue;
      }
      if (!res.ok) {
        const body = await res.text().catch(() => "");
        throw new Error(`TypeSafe ${res.status}: ${body}`);
      }
      return (await res.json()) as TypeSafeResponse;
    }
    throw new Error("TypeSafe request exhausted retries (rate limit / overload).");
  }
}

/** Shared singleton so consecutive askTypeSafe() calls keep rotating the pool. */
let sharedClient: TypeSafeRotatingClient | null = null;

/** Convenience: one-off call without holding a client instance.
 *  Uses a module-level singleton — the key cursor persists across calls,
 *  so repeated invocations genuinely round-robin through the key pool. */
export async function askTypeSafe(
  state: unknown,
  questions: Record<string, unknown>
): Promise<TypeSafeResponse> {
  if (!sharedClient) sharedClient = new TypeSafeRotatingClient();
  return sharedClient.systemOne(state, questions);
}
