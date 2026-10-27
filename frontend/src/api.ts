import type { Movie } from './types'
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init })
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try { const body = await res.json(); message = body.detail || message } catch {}
    throw new Error(message)
  }
  return res.json()
}
export async function collection(name: 'trending'|'popular'|'top-rated') { return request<{items: Movie[], source: string}>(`/movies/${name}`) }
export async function searchMovies(q: string, genre = 'All Movies') {
  const data = await request<{items: Movie[], source: string}>(`/movies/search?q=${encodeURIComponent(q)}`)
  const wanted = genre.toLowerCase() === 'sci-fi' ? 'science fiction' : genre.toLowerCase()
  if (!genre || genre === 'All Movies') return data
  return { ...data, items: data.items.filter(m => (m.genre_names || m.genres || []).some(g => g.toLowerCase() === wanted)) }
}
export async function getMovie(id: string|number) { return request<Movie>(`/movies/${id}`) }
export async function similarMovies(id: string|number) { return request<{items: Movie[], algorithm: string}>(`/recommendations/${id}`) }
export async function personalized(genres: string[], liked_movie_ids: string[]) {
  return request<{items: Movie[], algorithm: string}>('/recommendations/personalized', { method: 'POST', body: JSON.stringify({genres, liked_movie_ids, limit: 10}) })
}
export async function filterMovies(genre: string, q = '') {
  const params = new URLSearchParams()
  if (genre && genre !== 'All Movies') params.set('genre', genre)
  if (q) params.set('q', q)
  return request<{items: Movie[], total: number}>(`/movies?${params}`)
}
export async function health() { return request<{status: string, tmdb_enabled: boolean, catalog_size: number}>('/health') }
