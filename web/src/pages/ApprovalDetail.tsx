import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiFetch from '../api'

export default function ApprovalDetail(){
  const { id } = useParams()
  const navigate = useNavigate()
  const [approval, setApproval] = useState<any | null>(null)
  const [actions, setActions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [comment, setComment] = useState('')

  useEffect(()=>{
    if (!id) return
    setLoading(true)
    apiFetch(`/api/approvals/${id}`).then(async res => {
      if (!res.ok){ setError('Failed to fetch'); setLoading(false); return }
      const data = await res.json()
      setApproval(data)
      setActions(data.actions || [])
      setLoading(false)
    }).catch(e => { setError(String(e)); setLoading(false) })
  },[id])

  async function doAction(kind: 'approve' | 'reject'){
    if (!id) return
    const payload = { comment }
    const res = await apiFetch(`/api/approvals/${id}/${kind}`, { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok){
      const txt = await res.text()
      setError('Action failed: ' + txt)
      return
    }
    // refresh
    const refreshed = await (await apiFetch(`/api/approvals/${id}`)).json()
    setApproval(refreshed)
    setActions(refreshed.actions || [])
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!approval) return <div>Approval not found</div>

  return (
    <div>
      <h2>Approval #{approval.id}</h2>
      <div>Payment: {approval.payment_id}</div>
      <div>Status: {approval.status}</div>
      <div>Required Roles: {(approval.required_roles || []).join(', ')}</div>
      <h3>Actions</h3>
      <ul>
        {actions.map(a => <li key={a.id}>{a.action} by user {a.user_id} at {a.created_at} {a.comment ? ` — ${a.comment}` : ''}</li>)}
      </ul>

      <div style={{ marginTop: 20 }}>
        <textarea placeholder="Comment" value={comment} onChange={e => setComment(e.target.value)} style={{ width: '100%', minHeight: 80 }} />
        <div style={{ marginTop: 10 }}>
          <button onClick={() => doAction('approve')} style={{ marginRight: 8 }}>Approve</button>
          <button onClick={() => doAction('reject')}>Reject</button>
        </div>
      </div>
    </div>
  )
}
