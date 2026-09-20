import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  const cookieStore = await cookies();
  const next = request.nextUrl.searchParams.get("next");
  const destination = next === "/auth/reset-password" ? next : "/onboarding";
  const response = NextResponse.redirect(new URL(code ? destination : "/auth/sign-in?error=confirmation", request.url));

  if (!code || !url || !key) return response;

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll: () => cookieStore.getAll(),
      setAll: (values) => values.forEach(({ name, value, options }) => {
        cookieStore.set(name, value, options);
        response.cookies.set(name, value, options);
      }),
    },
  });
  const { error } = await supabase.auth.exchangeCodeForSession(code);

  if (error) return NextResponse.redirect(new URL("/auth/sign-in?error=confirmation", request.url));
  return response;
}
