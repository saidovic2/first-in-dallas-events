'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { statsApi } from '@/lib/api'
import { Calendar, TrendingUp, Database, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await statsApi.get()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your event management system</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Events This Week</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.events_this_week || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.total_events || 0} total events
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Extractions</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_extractions || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.extraction_success_rate || 0}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sources</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_sources || 0}</div>
            <p className="text-xs text-muted-foreground">
              Monitoring event sources
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Tasks</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.failed_tasks || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Events by Status */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Events by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.events_by_status && Object.entries(stats.events_by_status).map(([status, count]: [string, any]) => (
                <div key={status} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${status === 'published' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                    <span className="text-sm font-medium capitalize">{status}</span>
                  </div>
                  <span className="text-sm font-bold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Cities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.events_by_city?.slice(0, 5).map((item: any) => (
                <div key={item.city} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.city}</span>
                  <span className="text-sm font-bold">{item.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Sources */}
      <Card>
        <CardHeader>
          <CardTitle>Top Event Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats?.top_sources?.map((source: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm font-medium truncate max-w-md">{source.url}</span>
                <span className="text-sm font-bold">{source.count} events</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Errors */}
      {stats?.recent_errors && stats.recent_errors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Errors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recent_errors.map((error: any) => (
                <div key={error.task_id} className="border-l-4 border-red-500 pl-4 py-2">
                  <div className="text-sm font-medium text-gray-900">{error.url}</div>
                  <div className="text-xs text-red-600 mt-1">{error.error}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {error.timestamp ? new Date(error.timestamp).toLocaleString() : 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
