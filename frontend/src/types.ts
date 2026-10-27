export type Movie = {
  id: number | string; title: string; release_date?: string; year?: string | number | null;
  genres?: string[]; genre_names?: string[]; overview?: string; rating?: number | null;
  poster_path?: string | null; backdrop_path?: string | null; runtime?: number | null;
  similarity?: number; recommendation_reason?: string; source?: string;
}
