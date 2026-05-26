'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Check, Loader2, Calendar } from 'lucide-react'
import { submissionsApi } from '@/lib/api'

type PublishState = 'polling' | 'published' | 'timeout'

export default function SubmitSuccessPage() {
  const params = useSearchParams()
  const eventId = params.get('event_id')
  const [state, setState] = useState<PublishState>('polling')
  const [attempts, setAttempts] = useState(0)

  // Poll the submission endpoint until status becomes PUBLISHED or we give up.
  // Stripe webhooks typically fire within 2-5 seconds of checkout completion.
  useEffect(() => {
    if (!eventId) {
      setState('published') // no ID to check — show success anyway
      return
    }

    let cancelled = false
    const MAX_ATTEMPTS = 12  // 12 × 3 s = 36 s max wait
    const INTERVAL_MS = 3000

    async function poll() {
      if (cancelled) return
      try {
        const res = await submissionsApi.getById(eventId!)
        const status: string = res.data?.status ?? ''
        if (status === 'PUBLISHED') {
          if (!cancelled) setState('published')
          return
        }
      } catch {
        // submission endpoint may 404 briefly — keep polling
      }

      const next = attempts + 1
      setAttempts(next)
      if (next >= MAX_ATTEMPTS) {
        if (!cancelled) setState('timeout')
        return
      }
      setTimeout(poll, INTERVAL_MS)
    }

    poll()
    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
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
              Payment confirmed. We're activating your listing now — this only takes a moment.
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
            <CardContent className="space-y-4 text-center">
              <p className="text-sm text-gray-600">
                Your event has been published to the First in Dallas events calendar.
              </p>
              <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
                <Button asChild>
                  <Link href="/dashboard">
                    <Calendar className="mr-2 h-4 w-4" />
                    View my events
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/submit">Submit another event</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {state === 'timeout' && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-amber-100">
                <Check className="h-7 w-7 text-amber-600" />
              </div>
              <CardTitle>Payment received — publishing in progress</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-center">
              <p className="text-sm text-gray-600">
                Your payment was successful. Your event is being activated and should appear in the
                calendar within a few minutes. Check your dashboard for the updated status.
              </p>
              <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
                <Button asChild>
                  <Link href="/dashboard">
                    <Calendar className="mr-2 h-4 w-4" />
                    View my events
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
