'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { supabase } from '@/lib/supabase'
import { eventsApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { CheckCircle, XCircle, Clock, ExternalLink, Eye, Loader2 } from 'lucide-react'
import Image from 'next/image'

export default function SubmissionsPage() {
  const [submissions, setSubmissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'published' | 'rejected'>('pending')

  useEffect(() => {
    loadSubmissions()
  }, [filter])

  const loadSubmissions = async () => {
    try {
      let query = supabase
        .from('event_submissions')
        .select('*')
        .order('created_at', { ascending: false })

      if (filter !== 'all') {
        query = query.eq('status', filter)
      }

      const { data, error } = await query

      if (error) {
        console.error('Supabase error:', error)
        throw error
      }
      
      console.log('Loaded submissions:', data)
      console.log('Current filter:', filter)
      console.log('Submissions count:', data?.length || 0)
      
      // Log the actual status values we're seeing
      if (data && data.length > 0) {
        console.log('Status values in data:', data.map(s => s.status))
      }
      
      setSubmissions(data || [])
    } catch (error) {
      console.error('Failed to load submissions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id: string) => {
    if (!confirm('Approve and publish this event to the live directory?')) return
    
    try {
      // Get the submission details
      const { data: submission, error: fetchError } = await supabase
        .from('event_submissions')
        .select('*')
        .eq('id', id)
        .single()

      if (fetchError) throw fetchError

      // Create event in live directory via API
      await eventsApi.create({
        title: submission.title,
        primary_url: submission.primary_url || '',
        country: submission.country || 'USA',
        venue: submission.venue || '',
        address: submission.address || '',
        city: submission.city,
        state: submission.state || '',
        zip_code: submission.zip_code || '',
        start_at: submission.start_date,
        end_at: submission.end_date || null,
        price_amount: submission.price ? parseFloat(submission.price) : null,
        price_tier: submission.price_tier?.toUpperCase() || 'FREE',
        image_url: submission.image_url || '',
        description: submission.description,
        status: 'PUBLISHED',
        category: submission.submission_type === 'paid' ? 'FEATURED' : 'STANDARD',
        source_type: 'ORGANIZER_SUBMISSION',
        format: submission.format?.toUpperCase() || 'IN_PERSON'
      })

      // Update submission status in Supabase
      const { error } = await supabase
        .from('event_submissions')
        .update({ 
          status: 'published',
          published_at: new Date().toISOString()
        })
        .eq('id', id)

      if (error) throw error
      
      loadSubmissions()
      alert('✅ Event approved and published to live directory!')
    } catch (error: any) {
      console.error('Failed to approve:', error)
      alert(`Failed to approve event: ${error.message || 'Unknown error'}`)
    }
  }

  const handleReject = async (id: string) => {
    const reason = prompt('Reason for rejection:')
    if (!reason) return

    try {
      const { error } = await supabase
        .from('event_submissions')
        .update({ 
          status: 'rejected',
          admin_notes: reason
        })
        .eq('id', id)

      if (error) throw error
      
      loadSubmissions()
      alert('Event rejected')
    } catch (error) {
      console.error('Failed to reject:', error)
      alert('Failed to reject event')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  const pendingCount = submissions.filter(s => s.status === 'pending').length

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Organizer Submissions</h1>
          <p className="text-gray-600 mt-1">Review and approve events submitted by organizers</p>
        </div>
        {pendingCount > 0 && (
          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300 px-4 py-2 text-base">
            {pendingCount} Pending Review
          </Badge>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={filter === 'pending' ? 'default' : 'outline'}
          onClick={() => setFilter('pending')}
        >
          <Clock className="h-4 w-4 mr-2" />
          Pending ({submissions.filter(s => s.status === 'pending').length})
        </Button>
        <Button
          variant={filter === 'published' ? 'default' : 'outline'}
          onClick={() => setFilter('published')}
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          Published
        </Button>
        <Button
          variant={filter === 'rejected' ? 'default' : 'outline'}
          onClick={() => setFilter('rejected')}
        >
          <XCircle className="h-4 w-4 mr-2" />
          Rejected
        </Button>
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All ({submissions.length})
        </Button>
      </div>

      {/* Submissions List */}
      {submissions.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No submissions found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {submissions.map((submission) => (
            <Card key={submission.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex gap-6">
                  {/* Image */}
                  {submission.image_url && (
                    <div className="relative w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden">
                      <Image
                        src={submission.image_url}
                        alt={submission.title}
                        fill
                        className="object-cover"
                      />
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{submission.title}</h3>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {formatDateTime(submission.start_at)}
                          </span>
                          {submission.city && (
                            <span>📍 {submission.city}</span>
                          )}
                          {submission.category && (
                            <Badge variant="secondary" className="capitalize">
                              {submission.category.toLowerCase()}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Status Badge */}
                      <Badge
                        className={`${
                          submission.status === 'pending'
                            ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                            : submission.status === 'published'
                            ? 'bg-green-100 text-green-800 border-green-300'
                            : 'bg-red-100 text-red-800 border-red-300'
                        } border px-3 py-1`}
                      >
                        {submission.status.toUpperCase()}
                      </Badge>
                    </div>

                    {/* Description */}
                    {submission.description && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {submission.description}
                      </p>
                    )}

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      {submission.venue && (
                        <div>
                          <span className="text-gray-500">Venue:</span>
                          <span className="ml-2 font-medium">{submission.venue}</span>
                        </div>
                      )}
                      {submission.price_tier && (
                        <div>
                          <span className="text-gray-500">Price:</span>
                          <span className="ml-2 font-medium capitalize">
                            {submission.price_tier}
                            {submission.price_amount && ` - $${submission.price_amount}`}
                          </span>
                        </div>
                      )}
                      <div>
                        <span className="text-gray-500">Submitted:</span>
                        <span className="ml-2 font-medium">
                          {new Date(submission.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Type:</span>
                        <span className="ml-2 font-medium capitalize">
                          {submission.category === 'PAID' ? 'Featured' : 'Standard'}
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3">
                      {submission.source_url && (
                        <a
                          href={submission.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          View Event Page
                        </a>
                      )}
                      
                      {submission.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleApprove(submission.id)}
                            className="bg-green-600 hover:bg-green-700 text-white"
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Approve & Publish to Live
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleReject(submission.id)}
                            className="text-red-600 border-red-300 hover:bg-red-50"
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Reject
                          </Button>
                        </>
                      )}
                      
                      {submission.status === 'published' && (
                        <span className="text-sm text-green-600 flex items-center">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Published to Live Directory
                        </span>
                      )}
                      
                      {submission.status === 'rejected' && submission.admin_notes && (
                        <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md">
                          <strong>Rejection Reason:</strong> {submission.admin_notes}
                        </div>
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
