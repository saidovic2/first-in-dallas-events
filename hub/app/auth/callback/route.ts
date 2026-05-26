import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createRouteHandlerClient({ cookies })
    const { data: { session } } = await supabase.auth.exchangeCodeForSession(code)
    
    // Organizer row is created automatically by the handle_new_user DB trigger
    // when the user is first added to auth.users — no client-side insert needed.
  }

  // Redirect to dashboard on the same domain the callback was called from
  return NextResponse.redirect(new URL('/dashboard', requestUrl.origin))
}
