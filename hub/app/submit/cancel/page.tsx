'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { XCircle, ArrowLeft } from 'lucide-react'

export default function SubmitCancelPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50"><Nav /><div className="max-w-lg mx-auto pt-20 px-4 text-center text-gray-500">Loading…</div></div>}>
      <CancelContent />
    </Suspense>
  )
}

function CancelContent() {
  const params = useSearchParams()
  const eventId = params.get('event_id')

  // Build the return URL so the user can pick up where they left off.
  // The submit page doesn't yet support deep-linking to a saved draft,
  // so we send them back to /submit. The PENDING event remains in the DB
  // and can be paid later from the dashboard.
  const returnHref = '/submit'

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <div className="max-w-lg mx-auto pt-20 px-4">
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gray-100">
              <XCircle className="h-7 w-7 text-gray-500" />
            </div>
            <CardTitle>Payment cancelled</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-center">
            <p className="text-sm text-gray-600">
              No charge was made. Your event details have been saved and are waiting to be
              published — you can complete payment any time from your dashboard.
            </p>
            {eventId && (
              <p className="text-xs text-gray-400">Event ID: {eventId}</p>
            )}
            <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
              <Button asChild>
                <Link href="/dashboard">View my events</Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href={returnHref}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Submit a new event
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
