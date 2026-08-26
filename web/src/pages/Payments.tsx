import React, {useEffect, useState} from 'react'

export default function Payments(){
  const [payments, setPayments] = useState<any[]>([])

  useEffect(()=>{ fetchPayments() },[])
  function fetchPayments(){
    import('../api').then(({default: apiFetch})=>{
      apiFetch('/api/payments').then(r=>r.json()).then(setPayments).catch(()=>setPayments([]))
    })
  }

  async function hold(id:number){
    const apiFetch = (await import('../api')).default
    const res = await apiFetch(`/api/payments/${id}/hold`, { method: 'POST', body: JSON.stringify({ reason: 'Automated hold (demo)' }) })
    if (res.ok) fetchPayments()
  }

  return (
    <div style={{padding:20}}>
      <h2>Payments</h2>
      <ul>
        {payments.map(p=> (
          <li key={p.id}><a href={`/payments/${p.id}`}>#{p.id}</a> — {p.amount} — {p.status} <button onClick={()=>hold(p.id)}>Hold</button></li>
        ))}
      </ul>
    </div>
  )
}
