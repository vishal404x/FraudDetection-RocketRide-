import React, { useEffect, useState } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Approvals from './pages/Approvals'
import ApprovalDetail from './pages/ApprovalDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import Notifications from './pages/Notifications'
import apiFetch from './api'

export default function App(){
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  const [unread, setUnread] = useState(0)

  async function loadCount(){
    if (!token) { setUnread(0); return }
    try{
      const res = await apiFetch('/api/notifications')
      if (!res.ok) { setUnread(0); return }
      const data = await res.json()
      const u = (data || []).filter((n:any)=>!n.seen).length
      setUnread(u)
    }catch(e){ setUnread(0) }
  }

  useEffect(()=>{ loadCount() }, [token])

  return (
    <div style={{ padding: 20 }}>
      <header style={{ marginBottom: 20 }}>
        <h1>AP Payment Fraud Sentinel</h1>
        <nav>
          <Link to="/">Home</Link> | <Link to="/approvals">Approvals</Link> | <Link to="/notifications">Notifications{unread ? ` (${unread})` : ''}</Link> | {token ? <a href="#" onClick={()=>{ localStorage.removeItem('token'); window.location.href = '/login' }}>Logout</a> : <><Link to="/login">Login</Link> | <Link to="/register">Register</Link></>}
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/approvals" element={<Approvals/>} />
          <Route path="/approvals/:id" element={<ApprovalDetail/>} />
          <Route path="/login" element={<Login/>} />
          <Route path="/register" element={<Register/>} />
          <Route path="/notifications" element={<Notifications/>} />
          <Route path="/" element={<div>Welcome to Sentinel. Go to <Link to="/approvals">Approvals</Link></div>} />
        </Routes>
      </main>
    </div>
  )
}
