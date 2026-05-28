'use client'

import { Suspense, useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Check, Loader2 } from 'lucide-react'
import { submissionsApi } from '@/lib/api'

type PublishState = 'polling' | 'published' | 'timeout'

export default function SubmitSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50">
        <Nav />
        <div className="max-w-lg mx-auto pt-20 px-4 text-center text-gray-500">Loading…</div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  )
}

function SuccessContent() {
  const router = useRouter()
  const params = useSearchParams()
  const eventId = params.get('event_id')
  const [state, setState] = useState<PublishState>('polling')
  const attemptRef = useRef(0)  // ref avoids stale-closure bug with useState

  // Auto-redirect to dashboard once published (or on timeout)
  useEffect(() => {
    if (state === 'published' || state === 'timeout') {
      const t = setTimeout(() => router.replace('/submissions'), 2500)
      return () => clearTimeout(t)
    }
  }, [state, router])

  // Poll Railway API until event status is PUBLISHED
  useEffect(() => {
    if (!eventId) { setState('published'); return }

    const MAX = 12        // 12 × 3 s = 36 s
    const INTERVAL = 3000
    let cancelled = false

    async function poll() {
      if (cancelled) return
      try {
        const res = await submissionsApi.getById(eventId!)
        const status: string = (res.data?.status ?? '').toUpperCase()
        if (status === 'PUBLISHED') {
          if (!cancelled) setState('published')
          return
        }
      } catch { /* 404 briefly after redirect — keep going */ }

      attemptRef.current += 1
      if (attemptRef.current >= MAX) {
        if (!cancelled) setState('timeout')
        return
      }
      setTimeout(poll, INTERVAL)
    }

    poll()
    return () => { cancelled = true }
  }, [eventId])

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <div className="max-w-lg mx-auto pt-20 px-4">

        {state === 'polling' && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
                <Loader2 className="h-7 w-7 text-blue-600 animate-spin" />
              </div>
              <CardTitle>Publishing your event…</CardTitle>
            </CardHeader>
            <CardContent className="text-center text-sm text-gray-500">
              Payment confirmed. Activating your listing — this only takes a moment.
            </CardContent>
          </Card>
        )}

        {state === 'published' && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
                <Check className="h-7 w-7 text-green-600" />
              </div>
              <CardTitle>Your event is live!</CardTitle>
            </CardHeader>
            <CardContent className="text-center text-sm text-gray-500">
              Taking you to your dashboard…
            </CardContent>
          </Card>
        )}

        {state === 'timeout' && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-amber-100">
                <Check className="h-7 w-7 text-amber-600" />
              </div>
              <CardTitle>Payment received</CardTitle>
            </CardHeader>
            <CardContent className="text-center text-sm text-gray-500">
              Your event is being activated. Taking you to your dashboard…
            </CardContent>
          </Card>
        )}

      </div>
    </div>
  )
}
