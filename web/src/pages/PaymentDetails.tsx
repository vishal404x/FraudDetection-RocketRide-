import React, {useEffect, useState} from 'react'
import {useParams} from 'react-router-dom'

export default function PaymentDetails(){
  const { id } = useParams()
  const [payment, setPayment] = useState<any>(null)

  useEffect(()=>{ if (id) fetchPayment() },[id])
  function fetchPayment(){
    import('../api').then(({default: apiFetch})=>{
      apiFetch('/api/payments/' + id).then(r=>r.json()).then(setPayment).catch(()=>setPayment(null))
    })
  }

  async function release(){
    const apiFetch = (await import('../api')).default
    const res = await apiFetch(`/api/payments/${id}/release`, { method: 'POST', body: JSON.stringify({ reason: 'Verified by AP' }) })
    if (res.ok) fetchPayment()
  }

  async function reject(){
    const apiFetch = (await import('../api')).default
    const res = await apiFetch(`/api/payments/${id}/reject`, { method: 'POST', body: JSON.stringify({ reason: 'Rejected after verification' }) })
    if (res.ok) fetchPayment()
  }

  if (!payment) return <div style={{padding:20}}>Loading payment...</div>

  return (
    <div style={{padding:20}}>
      <h2>Payment #{payment.id}</h2>
      <div>Amount: {payment.amount}</div>
      <div>Status: {payment.status}</div>
      <div>Held: {payment.held}</div>
      <div>Reason: {payment.reason}</div>
      <button onClick={release}>Release</button>
      <button onClick={reject}>Reject</button>
    </div>
  )
}
