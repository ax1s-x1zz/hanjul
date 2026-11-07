import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

import { isSupabaseEnabled, supabaseAnonKey, supabaseUrl } from "./config";

export async function getSupabaseServer() {
  if (!isSupabaseEnabled) return null;
  const cookieStore = await cookies();

  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (items) => {
        try {
          items.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options),
          );
        } catch {
          // Called from a Server Component; middleware handles refresh.
        }
      },
    },
  });
}
