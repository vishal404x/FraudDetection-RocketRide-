const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function apiFetch(path: string, opts: any = {}){
  const token = localStorage.getItem('token')
  const headers = Object.assign({'Content-Type': 'application/json'}, opts.headers || {})
  if (token) headers['Authorization'] = 'Bearer ' + token
  const res = await fetch(BASE + path, Object.assign({}, opts, { headers }))
  return res
}

export default apiFetch
