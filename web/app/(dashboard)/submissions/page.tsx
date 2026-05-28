'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { submissionsApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { CheckCircle, XCircle, Clock, ExternalLink, Loader2 } from 'lucide-react'
import Image from 'next/image'

export default function SubmissionsPage() {
  const [allSubmissions, setAllSubmissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'published' | 'rejected'>('all')
  const [acting, setActing] = useState<number | null>(null)
  const searchParams = useSearchParams()
  const organizerFilter = searchParams.get('organizer')

  useEffect(() => {
    loadSubmissions()
  }, [])

  const loadSubmissions = async () => {
    try {
      const res = await submissionsApi.list()
      let data = res.data || []
      if (organizerFilter) {
        data = data.filter((s: any) => s.organizer_email === organizerFilter)
      }
      setAllSubmissions(data)
    } catch (error) {
      console.error('Failed to load submissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const filtered = filter === 'all'
    ? allSubmissions
    : allSubmissions.filter(s => s.status === filter)

  const handleApprove = async (id: number) => {
    if (!confirm('Approve and publish this event to the live directory?')) return
    setActing(id)
    try {
      await submissionsApi.approve(id)
      await loadSubmissions()
      alert('✅ Event approved and published!')
    } catch (error: any) {
      alert(`Failed to approve: ${error.response?.data?.detail || error.message}`)
    } finally {
      setActing(null)
    }
  }

  const handleReject = async (id: number) => {
    const reason = prompt('Reason for rejection:')
    if (!reason) return
    setActing(id)
    try {
      await submissionsApi.reject(id, reason)
      await loadSubmissions()
    } catch (error: any) {
      alert(`Failed to reject: ${error.response?.data?.detail || error.message}`)
    } finally {
      setActing(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    )
  }

  const counts = {
    pending: allSubmissions.filter(s => s.status === 'pending').length,
    published: allSubmissions.filter(s => s.status === 'published').length,
    rejected: allSubmissions.filter(s => s.status === 'rejected').length,
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Organizer Submissions</h1>
          <p className="text-gray-600 mt-1">
            {organizerFilter
              ? `Viewing submissions from: ${organizerFilter}`
              : 'Review and approve events submitted by organizers'}
          </p>
        </div>
        {counts.pending > 0 && (
          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300 px-4 py-2 text-base">
            {counts.pending} Pending Review
          </Badge>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {(['pending', 'published', 'rejected', 'all'] as const).map((f) => (
          <Button
            key={f}
            variant="outline"
            onClick={() => setFilter(f)}
            className={filter === f ? 'bg-blue-500 text-white border-blue-600' : ''}
          >
            {f === 'pending' && <Clock className="h-4 w-4 mr-2" />}
            {f === 'published' && <CheckCircle className="h-4 w-4 mr-2" />}
            {f === 'rejected' && <XCircle className="h-4 w-4 mr-2" />}
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f !== 'all' && ` (${counts[f] ?? allSubmissions.length})`}
            {f === 'all' && ` (${allSubmissions.length})`}
          </Button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            No {filter === 'all' ? '' : filter} submissions found
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filtered.map((submission) => (
            <Card key={submission.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex gap-6">
                  {submission.image_url && (
                    <div className="relative w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden">
                      <Image src={submission.image_url} alt={submission.title} fill className="object-cover" />
                    </div>
                  )}

                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{submission.title}</h3>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                          {submission.start_at && (
                            <span className="flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              {formatDateTime(submission.start_at)}
                            </span>
                          )}
                          {submission.city && <span>📍 {submission.city}</span>}
                          {submission.organizer_email && (
                            <span className="text-gray-400">by {submission.organizer_email}</span>
                          )}
                        </div>
                      </div>
                      <Badge className={`border px-3 py-1 ${
                        submission.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                          : submission.status === 'published'
                          ? 'bg-green-100 text-green-800 border-green-300'
                          : 'bg-red-100 text-red-800 border-red-300'
                      }`}>
                        {submission.status.toUpperCase()}
                      </Badge>
                    </div>

                    {submission.description && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">{submission.description}</p>
                    )}

                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      {submission.venue && (
                        <div><span className="text-gray-500">Venue:</span><span className="ml-2 font-medium">{submission.venue}</span></div>
                      )}
                      {submission.price_tier && (
                        <div>
                          <span className="text-gray-500">Price:</span>
                          <span className="ml-2 font-medium capitalize">
                            {submission.price_tier}{submission.price_amount ? ` — $${submission.price_amount}` : ''}
                          </span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-500">Submitted:</span>
                        <span className="ml-2 font-medium">{new Date(submission.created_at).toLocaleDateString()}</span>
                      </div>
                      {submission.is_featured && (
                        <div><span className="text-amber-600 font-medium">⭐ Featured listing</span></div>
                      )}
                    </div>

                    <div className="flex items-center gap-3">
                      {(submission.wp_url || submission.source_url) && (
                        <a href={submission.wp_url || submission.source_url} target="_blank" rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-700 flex items-center">
                          <ExternalLink className="h-4 w-4 mr-1" />
                          {submission.wp_url ? 'View on First in Dallas' : 'View Event Page'}
                        </a>
                      )}

                      {submission.status === 'pending' && (
                        <>
                          <Button size="sm" disabled={acting === submission.id}
                            onClick={() => handleApprove(submission.id)}
                            className="bg-green-600 hover:bg-green-700 text-white">
                            {acting === submission.id
                              ? <Loader2 className="h-4 w-4 animate-spin" />
                              : <><CheckCircle className="h-4 w-4 mr-1" />Approve & Publish</>}
                          </Button>
                          <Button size="sm" variant="outline" disabled={acting === submission.id}
                            onClick={() => handleReject(submission.id)}
                            className="text-red-600 border-red-300 hover:bg-red-50">
                            <XCircle className="h-4 w-4 mr-1" />Reject
                          </Button>
                        </>
                      )}

                      {submission.status === 'published' && (
                        <span className="text-sm text-green-600 flex items-center">
                          <CheckCircle className="h-4 w-4 mr-1" />Published to live calendar
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
