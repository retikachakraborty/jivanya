import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !key) return NextResponse.next();
  const response = NextResponse.next({ request });
  const supabase = createServerClient(url, key, { cookies: { getAll: () => request.cookies.getAll(), setAll: (cookies) => cookies.forEach(({ name, value, options }) => response.cookies.set(name, value, options)) } });
  const { data: { user } } = await supabase.auth.getUser();
  if (request.nextUrl.pathname.startsWith("/app") || request.nextUrl.pathname === "/onboarding") {
    if (!user) return NextResponse.redirect(new URL("/auth/sign-in", request.url));
  }
  if (user && request.nextUrl.pathname.startsWith("/auth/") && request.nextUrl.pathname !== "/auth/callback" && !request.nextUrl.pathname.startsWith("/auth/reset-password")) return NextResponse.redirect(new URL("/app", request.url));
  return response;
}

export const config = { matcher: ["/app/:path*", "/onboarding", "/auth/:path*"] };
