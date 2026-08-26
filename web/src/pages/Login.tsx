import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import apiFetch from '../api'

export default function Login(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  async function submit(e: any){
    e.preventDefault()
    setError(null)
    try{
      const res = await apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
      if (!res.ok){
        const txt = await res.text()
        setError('Login failed: ' + txt)
        return
      }
      const data = await res.json()
      // backend returns access_token
      if (data.access_token){
        localStorage.setItem('token', data.access_token)
        navigate('/approvals')
      } else {
        setError('No token returned')
      }
    }catch(err:any){
      setError(String(err))
    }
  }

  return (
    <div style={{ maxWidth: 480 }}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label>
          <input value={email} onChange={e => setEmail(e.target.value)} />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        {error && <div style={{ color: 'red' }}>{error}</div>}
        <div style={{ marginTop: 10 }}>
          <button type="submit">Login</button>
          <Link style={{ marginLeft: 10 }} to="/register">Register</Link>
        </div>
      </form>
    </div>
  )
}
