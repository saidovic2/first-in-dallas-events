'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getStatusColor, getStatusLabel, formatDateTime } from '@/lib/utils'
import { Clock, CheckCircle, XCircle, ExternalLink, ChevronRight, AlertCircle } from 'lucide-react'
import Link from 'next/link'

export default function SubmissionsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [user, setUser] = useState<any>(null)
  const [submissions, setSubmissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showSuccess, setShowSuccess] = useState(false)

  useEffect(() => {
    if (searchParams.get('success') === 'true') {
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 5000)
    }
    checkUser()
  }, [searchParams])

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    
    if (!user) {
      router.push('/auth/login')
      return
    }

    setUser(user)
    await loadSubmissions(user.id)
    setLoading(false)
  }

  const loadSubmissions = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('event_submissions')
        .select('*')
        .eq('organizer_id', userId)
        .order('created_at', { ascending: false })

      if (error) throw error

      setSubmissions(data || [])
    } catch (error) {
      console.error('Error loading submissions:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'approved':
      case 'published':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Submissions</h1>
            <p className="text-gray-600 mt-2">Track the status of your event submissions</p>
          </div>
          <Link href="/submit">
            <Button>
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Submit New Event
            </Button>
          </Link>
        </div>

        {/* Success Message */}
        {showSuccess && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-green-900">Event Submitted Successfully!</h3>
              <p className="text-sm text-green-700 mt-1">
                Your event has been submitted for review. We'll review it within 24-48 hours.
              </p>
            </div>
          </div>
        )}

        {/* Submissions List */}
        {submissions.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="max-w-md mx-auto">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Submissions Yet</h3>
                <p className="text-gray-600 mb-6">
                  You haven't submitted any events yet. Get started by sharing your first event with the community.
                </p>
                <Link href="/submit">
                  <Button>Submit Your First Event</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {submissions.map((submission) => (
              <Card key={submission.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    {/* Status Icon */}
                    <div className="flex-shrink-0 pt-1">
                      {getStatusIcon(submission.status)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-1">
                            {submission.title}
                          </h3>
                          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                            <span className="flex items-center">
                              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              {submission.city || 'Location TBD'}
                            </span>
                            {submission.start_date && (
                              <span className="flex items-center">
                                <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                {formatDateTime(submission.start_date)}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Status Badge */}
                        <div className="flex-shrink-0">
                          <Badge className={`${getStatusColor(submission.status)} border px-3 py-1`}>
                            {getStatusLabel(submission.status)}
                          </Badge>
                        </div>
                      </div>

                      {/* Submission Details */}
                      <div className="flex flex-wrap items-center gap-4 text-sm mb-3">
                        <span className="text-gray-600">
                          Type: <span className="font-medium capitalize">{submission.submission_type}</span>
                        </span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-600">
                          Submitted: {new Date(submission.created_at).toLocaleDateString()}
                        </span>
                        {submission.format && (
                          <>
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-600 capitalize">{submission.format}</span>
                          </>
                        )}
                      </div>

                      {/* Description Preview */}
                      {submission.description && (
                        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                          {submission.description}
                        </p>
                      )}

                      {/* Admin Notes (if rejected) */}
                      {submission.status === 'rejected' && submission.admin_notes && (
                        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-3">
                          <p className="text-sm text-red-800">
                            <strong>Rejection Reason:</strong> {submission.admin_notes}
                          </p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-3">
                        {/* Pending Event - Show message inline */}
                        {submission.status === 'pending' && (
                          <div className="text-sm text-yellow-700 bg-yellow-50 px-3 py-2 rounded-md flex items-center">
                            <Clock className="h-3.5 w-3.5 mr-2 flex-shrink-0" />
                            This event is under review and not yet visible to the public
                          </div>
                        )}

                        {/* Published Event - Show link and live status */}
                        {submission.status === 'published' && (
                          <>
                            {submission.primary_url && (
                              <a
                                href={submission.primary_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                              >
                                View Event Page
                                <ExternalLink className="h-3.5 w-3.5 ml-1" />
                              </a>
                            )}
                            <span className="text-sm text-green-600 flex items-center">
                              <CheckCircle className="h-3.5 w-3.5 mr-1" />
                              Live on calendar
                            </span>
                          </>
                        )}

                        {/* Rejected Event - Show message */}
                        {submission.status === 'rejected' && (
                          <div className="text-sm text-red-700 bg-red-50 px-3 py-2 rounded-md flex items-center">
                            <XCircle className="h-3.5 w-3.5 mr-2 flex-shrink-0" />
                            Event not published - see rejection reason above
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Arrow Icon */}
                    <div className="flex-shrink-0 pt-1">
                      <ChevronRight className="h-5 w-5 text-gray-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Info Card */}
        {submissions.length > 0 && (
          <Card className="mt-8 bg-blue-50 border-blue-200">
            <CardContent className="p-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <AlertCircle className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">About the Review Process</h3>
                  <ul className="space-y-1 text-sm text-blue-800">
                    <li>• <strong>Pending:</strong> Your event is being reviewed by our team</li>
                    <li>• <strong>Published:</strong> Your event is live on the First in Dallas calendar</li>
                    <li>• <strong>Rejected:</strong> Your event didn't meet our guidelines (see reason above)</li>
                  </ul>
                  <p className="text-sm text-blue-700 mt-3">
                    Review typically takes 24-48 hours. You'll be notified when your event status changes.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
