import React, { useEffect, useState } from 'react'
import apiFetch from '../api'
import { Link } from 'react-router-dom'

export default function Approvals(){
  const [approvals, setApprovals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(()=>{
    setLoading(true)
    apiFetch('/api/approvals').then(async res => {
      if (!res.ok){
        setError('Failed to load')
        setLoading(false)
        return
      }
      const data = await res.json()
      setApprovals(data)
      setLoading(false)
    }).catch(e => { setError(String(e)); setLoading(false) })
  },[])

  if (loading) return <div>Loading approvals...</div>
  if (error) return <div>Error: {error}</div>

  if (!approvals.length) return <div>No approval requests.</div>

  return (
    <div>
      <h2>Approval Requests</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Payment ID</th>
            <th>Status</th>
            <th>Required Roles</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {approvals.map(a => (
            <tr key={a.id} style={{ borderTop: '1px solid #ddd' }}>
              <td>{a.id}</td>
              <td>{a.payment_id}</td>
              <td>{a.status}</td>
              <td>{(a.required_roles || []).join(', ')}</td>
              <td>{a.created_at}</td>
              <td><Link to={`/approvals/${a.id}`}>View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
