'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { tasksApi } from '@/lib/api'
import { Plus, X, Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function AddEventsPage() {
  const [urls, setUrls] = useState<string[]>([''])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [error, setError] = useState('')

  const addUrlField = () => {
    setUrls([...urls, ''])
  }

  const removeUrlField = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index))
  }

  const updateUrl = (index: number, value: string) => {
    const newUrls = [...urls]
    newUrls[index] = value
    setUrls(newUrls)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResults([])
    setLoading(true)

    const validUrls = urls.filter(url => url.trim() !== '')

    if (validUrls.length === 0) {
      setError('Please enter at least one URL')
      setLoading(false)
      return
    }

    try {
      const response = await tasksApi.extract(validUrls)
      setResults(response.data)
      setUrls([''])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to queue extraction tasks')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Add Events</h1>
        <p className="text-gray-600 mt-1">Paste URLs to extract event information</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Extract Events from URLs</CardTitle>
          <CardDescription>
            Supports Facebook, Instagram, ICS files, RSS feeds, and webpages with event data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-3">
              {urls.map((url, index) => (
                <div key={index} className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      type="url"
                      placeholder="https://example.com/event"
                      value={url}
                      onChange={(e) => updateUrl(index, e.target.value)}
                    />
                  </div>
                  {urls.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removeUrlField(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={addUrlField}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Another URL
            </Button>

            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Extract Events'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Extraction Tasks Queued</CardTitle>
            <CardDescription>
              Tasks are being processed in the background
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="text-sm font-medium truncate">{task.url}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline">{task.source_type}</Badge>
                      <Badge variant={task.status === 'queued' ? 'secondary' : 'default'}>
                        {task.status}
                      </Badge>
                    </div>
                  </div>
                  {task.status === 'queued' && (
                    <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                  )}
                  {task.status === 'done' && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  {task.status === 'failed' && (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Supported Sources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">Facebook Events</div>
              <div className="text-xs text-muted-foreground mt-1">facebook.com/events/*</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">Instagram Posts</div>
              <div className="text-xs text-muted-foreground mt-1">instagram.com/p/*</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">ICS/iCal Files</div>
              <div className="text-xs text-muted-foreground mt-1">*.ics</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">RSS/Atom Feeds</div>
              <div className="text-xs text-muted-foreground mt-1">*/feed, *.xml</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">JSON-LD Events</div>
              <div className="text-xs text-muted-foreground mt-1">Structured data</div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">Generic Webpages</div>
              <div className="text-xs text-muted-foreground mt-1">Meta tags fallback</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
