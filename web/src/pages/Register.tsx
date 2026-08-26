import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import apiFetch from '../api'

export default function Register(){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  async function submit(e: any){
    e.preventDefault()
    setError(null)
    try{
      const res = await apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password, full_name: fullName }) })
      if (!res.ok){
        const txt = await res.text()
        setError('Register failed: ' + txt)
        return
      }
      const data = await res.json()
      // on success, some systems return token; if not, redirect to login
      if (data.access_token){
        localStorage.setItem('token', data.access_token)
        navigate('/approvals')
      } else {
        navigate('/login')
      }
    }catch(err:any){
      setError(String(err))
    }
  }

  return (
    <div style={{ maxWidth: 480 }}>
      <h2>Register</h2>
      <form onSubmit={submit}>
        <div>
          <label>Full name</label>
          <input value={fullName} onChange={e => setFullName(e.target.value)} />
        </div>
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
          <button type="submit">Register</button>
          <Link style={{ marginLeft: 10 }} to="/login">Login</Link>
        </div>
      </form>
    </div>
  )
}
