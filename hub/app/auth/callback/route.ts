import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createRouteHandlerClient({ cookies })
    const { data: { session } } = await supabase.auth.exchangeCodeForSession(code)
    
    // If user signed in with Google, create organizer profile if it doesn't exist
    if (session?.user) {
      const { data: existingProfile } = await supabase
        .from('organizers')
        .select('id')
        .eq('id', session.user.id)
        .single()
      
      // Create organizer profile for new Google users
      if (!existingProfile) {
        await supabase
          .from('organizers')
          .insert({
            id: session.user.id,
            email: session.user.email,
            full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || '',
            organization_name: '',
          })
      }
    }
  }

  // Redirect to dashboard on the same domain the callback was called from
  return NextResponse.redirect(new URL('/dashboard', requestUrl.origin))
}
