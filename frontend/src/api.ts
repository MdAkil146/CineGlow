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
export async function searchMovies(q: string, genre = 'All Movies', page = 1) {
  const params = new URLSearchParams({ q, page: String(page) })
  if (genre && genre !== 'All Movies') params.set('genre', genre)
  return request<{items: Movie[], source: string, page?: number, total?: number, total_pages?: number}>(`/movies/search?${params}`)
}
export async function getMovie(id: string|number) { return request<Movie>(`/movies/${id}`) }
export async function similarMovies(id: string|number) { return request<{items: Movie[], algorithm: string}>(`/recommendations/${id}`) }
export async function personalized(genres: string[], liked_movie_ids: string[]) {
  return request<{items: Movie[], algorithm: string}>('/recommendations/personalized', { method: 'POST', body: JSON.stringify({genres, liked_movie_ids, limit: 10}) })
}
export async function filterMovies(genre: string, q = '', page = 1) {
  const params = new URLSearchParams()
  if (genre && genre !== 'All Movies') params.set('genre', genre)
  if (q) params.set('q', q)
  params.set('page', String(page))
  return request<{items: Movie[], total: number, page?: number, total_pages?: number}>(`/movies?${params}`)
}
export async function health() { return request<{status: string, tmdb_enabled: boolean, catalog_size: number}>('/health') }
