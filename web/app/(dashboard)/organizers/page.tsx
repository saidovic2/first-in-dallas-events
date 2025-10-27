'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { supabase } from '@/lib/supabase'
import { Search, Users, FileText, CheckCircle, XCircle, Mail, Building, Calendar } from 'lucide-react'

interface Organizer {
  id: string
  email: string
  full_name: string
  organization_name: string
  created_at: string
  total_submissions: number
  pending_submissions: number
  published_submissions: number
  rejected_submissions: number
  last_submission_date?: string
}

export default function OrganizersPage() {
  const [organizers, setOrganizers] = useState<Organizer[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
  })

  useEffect(() => {
    loadOrganizers()
  }, [])

  const loadOrganizers = async () => {
    try {
      // Get all organizer submissions from Supabase
      const { data: submissions, error } = await supabase
        .from('event_submissions')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      
      if (!submissions) {
        setLoading(false)
        return
      }

      // Group submissions by organizer email
      const organizerMap = new Map<string, any>()

      submissions.forEach((submission: any) => {
        const email = submission.organizer_contact || 'unknown'
        
        if (!organizerMap.has(email)) {
          organizerMap.set(email, {
            id: email,
            email: email,
            full_name: submission.title?.split(' ')[0] || 'Unknown', // Extract from first event
            organization_name: submission.venue || 'N/A',
            created_at: submission.created_at,
            total_submissions: 0,
            pending_submissions: 0,
            published_submissions: 0,
            rejected_submissions: 0,
            last_submission_date: submission.created_at,
          })
        }

        const organizer = organizerMap.get(email)
        organizer.total_submissions++
        
        if (submission.status === 'PENDING') organizer.pending_submissions++
        if (submission.status === 'PUBLISHED') organizer.published_submissions++
        if (submission.status === 'REJECTED') organizer.rejected_submissions++
        
        // Update last submission date
        if (new Date(submission.created_at) > new Date(organizer.last_submission_date)) {
          organizer.last_submission_date = submission.created_at
        }
      })

      const organizersList = Array.from(organizerMap.values())
      setOrganizers(organizersList)

      // Calculate stats
      setStats({
        total: organizersList.length,
        active: organizersList.filter(o => o.total_submissions > 0).length,
        inactive: organizersList.filter(o => o.total_submissions === 0).length,
      })
    } catch (error) {
      console.error('Failed to load organizers:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredOrganizers = organizers.filter(org => 
    org.email.toLowerCase().includes(search.toLowerCase()) ||
    org.full_name.toLowerCase().includes(search.toLowerCase()) ||
    org.organization_name.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Organizers Management</h1>
        <p className="text-gray-600 mt-1">View and manage event organizers</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Organizers</CardTitle>
            <Users className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Organizers</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-gray-500">With submissions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Submissions</CardTitle>
            <FileText className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {organizers.reduce((sum, org) => sum + org.total_submissions, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            type="text"
            placeholder="Search organizers by name, email, or organization..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Organizers List */}
      {filteredOrganizers.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">
              {search ? 'No organizers found matching your search' : 'No organizers yet'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredOrganizers.map((organizer) => (
            <Card key={organizer.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  {/* Organizer Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                        <Users className="h-6 w-6 text-primary-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {organizer.full_name}
                        </h3>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Mail className="h-4 w-4" />
                          {organizer.email}
                        </div>
                      </div>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <div>
                        <p className="text-xs text-gray-500">Organization</p>
                        <div className="flex items-center gap-1 mt-1">
                          <Building className="h-4 w-4 text-gray-400" />
                          <p className="text-sm font-medium">{organizer.organization_name}</p>
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-xs text-gray-500">Total Submissions</p>
                        <p className="text-sm font-medium mt-1">{organizer.total_submissions}</p>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Status Breakdown</p>
                        <div className="flex gap-2 mt-1">
                          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300 border text-xs">
                            {organizer.pending_submissions} Pending
                          </Badge>
                          <Badge className="bg-green-100 text-green-800 border-green-300 border text-xs">
                            {organizer.published_submissions} Published
                          </Badge>
                        </div>
                      </div>

                      <div>
                        <p className="text-xs text-gray-500">Member Since</p>
                        <div className="flex items-center gap-1 mt-1">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <p className="text-sm font-medium">
                            {new Date(organizer.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Last Submission */}
                    {organizer.last_submission_date && (
                      <div className="mt-3 text-sm text-gray-600">
                        Last submission: {new Date(organizer.last_submission_date).toLocaleDateString()}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => window.location.href = `/submissions?organizer=${organizer.email}`}
                    >
                      <FileText className="h-4 w-4 mr-1" />
                      View Submissions
                    </Button>
                    
                    {organizer.rejected_submissions > 0 && (
                      <Badge variant="secondary" className="text-xs">
                        <XCircle className="h-3 w-3 mr-1" />
                        {organizer.rejected_submissions} Rejected
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Activity Summary */}
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Activity Level:</span>
                    <div className="flex items-center gap-2">
                      {organizer.total_submissions === 0 && (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                      {organizer.total_submissions >= 1 && organizer.total_submissions < 5 && (
                        <Badge className="bg-blue-100 text-blue-800 border-blue-300 border">Low Activity</Badge>
                      )}
                      {organizer.total_submissions >= 5 && organizer.total_submissions < 10 && (
                        <Badge className="bg-green-100 text-green-800 border-green-300 border">Active</Badge>
                      )}
                      {organizer.total_submissions >= 10 && (
                        <Badge className="bg-purple-100 text-purple-800 border-purple-300 border">Very Active</Badge>
                      )}
                      
                      {organizer.published_submissions > 0 && (
                        <span className="text-green-600 text-xs">
                          {Math.round((organizer.published_submissions / organizer.total_submissions) * 100)}% approval rate
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
