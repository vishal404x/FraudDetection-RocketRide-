import React, { useEffect, useState } from 'react'
import apiFetch from '../api'

export default function Notifications(){
  const [notifs, setNotifs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function load(){
    setLoading(true)
    try{
      const res = await apiFetch('/api/notifications')
      if (!res.ok){ setError('Failed to load'); setLoading(false); return }
      const data = await res.json()
      setNotifs(data)
    }catch(e:any){ setError(String(e)) }
    setLoading(false)
  }

  useEffect(()=>{ load() }, [])

  async function markSeen(id:any){
    await apiFetch(`/api/notifications/${id}/mark-seen`, { method: 'POST' })
    load()
  }

  if (loading) return <div>Loading notifications...</div>
  if (error) return <div>Error: {error}</div>
  if (!notifs.length) return <div>No notifications</div>

  return (
    <div>
      <h2>Notifications</h2>
      <ul>
        {notifs.map(n => (
          <li key={n.id} style={{ marginBottom: 8, background: n.seen ? '#fff' : '#eef', padding: 8 }}>
            <div><strong>{n.notif_type}</strong> — {n.message}</div>
            <div style={{ fontSize: 12, color: '#666' }}>{n.created_at}</div>
            {!n.seen && <button onClick={()=>markSeen(n.id)}>Mark seen</button>}
          </li>
        ))}
      </ul>
    </div>
  )
}
