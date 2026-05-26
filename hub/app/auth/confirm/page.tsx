'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mail } from 'lucide-react'

export default function ConfirmEmailPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
            <Mail className="h-7 w-7 text-blue-600" />
          </div>
          <CardTitle>Check your email</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-center">
          <p className="text-sm text-gray-600">
            We sent a confirmation link to your email address. Click the link to activate your
            account, then sign in.
          </p>
          <p className="text-xs text-gray-400">
            Didn't receive it? Check your spam folder or{' '}
            <Link href="/auth/signup" className="underline">
              try signing up again
            </Link>
            .
          </p>
          <Button variant="outline" asChild className="w-full">
            <Link href="/auth/login">Go to sign in</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
