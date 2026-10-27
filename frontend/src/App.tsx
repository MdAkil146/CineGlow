import { useEffect, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { Search, Sparkles, Film, Compass, SlidersHorizontal, X, Star, ArrowRight, Play, Menu, WandSparkles, Heart, RotateCcw, LoaderCircle, Clapperboard } from 'lucide-react'
import type { Movie } from './types'
import { collection, searchMovies, getMovie, similarMovies, personalized, filterMovies, health } from './api'

const genres = ['Action','Comedy','Horror','Romance','Thriller','Science Fiction','Adventure','Drama','Animation','Mystery']
const localPoster = (title: string) => {
  const safe = title.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="540" viewBox="0 0 360 540"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#d9c4ff"/><stop offset=".55" stop-color="#8060b6"/><stop offset="1" stop-color="#2b1d40"/></linearGradient><radialGradient id="r"><stop stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs><rect width="360" height="540" fill="url(#g)"/><circle cx="180" cy="190" r="175" fill="url(#r)"/><path d="M0 390 Q180 300 360 390 V540 H0Z" fill="#21172f" fill-opacity=".4"/><text x="180" y="420" text-anchor="middle" fill="#fff" font-family="Arial,sans-serif" font-size="23" font-weight="700">${safe.slice(0,28)}</text><text x="180" y="454" text-anchor="middle" fill="#f0e6ff" font-family="Arial,sans-serif" font-size="11" letter-spacing="4">CINEGLOW</text></svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

function poster(movie: Pick<Movie, 'title' | 'poster_path'>) {
  if (movie.poster_path?.startsWith('http')) return movie.poster_path
  if (movie.poster_path?.startsWith('/')) return `https://image.tmdb.org/t/p/w500${movie.poster_path}`
  return localPoster(movie.title)
}
function year(movie: Movie) { return movie.year || movie.release_date?.slice(0,4) || '' }
function rating(movie: Movie) { return typeof movie.rating === 'number' ? movie.rating.toFixed(1) : null }

function MovieCard({movie, onOpen, compact=false}: {movie: Movie, onOpen:(m:Movie)=>void, compact?:boolean}) {
  const reduce = useReducedMotion()
  return <motion.button className={`movie-card ${compact?'compact':''}`} onClick={()=>onOpen(movie)} whileHover={reduce?undefined:{y:-6, scale:1.015}} transition={{duration:.2}} aria-label={`View ${movie.title} details`}>
    <div className="poster-wrap"><img src={poster(movie)} alt={`${movie.title} poster`} loading="lazy" onError={e=>{(e.currentTarget as HTMLImageElement).src=localPoster(movie.title)}}/>
      <span className="poster-open"><Play size={16} fill="currentColor"/></span>
      {rating(movie) && <span className="rating"><Star size={12} fill="currentColor"/>{rating(movie)}</span>}
    </div>
    <div className="movie-meta"><strong>{movie.title}</strong><span>{year(movie)}{movie.genres?.[0] ? ` · ${movie.genres[0]}` : ''}</span></div>
  </motion.button>
}

function Section({title, subtitle, items, onOpen, action}: {title:string,subtitle?:string,items:Movie[],onOpen:(m:Movie)=>void,action?:ReactNode}) {
  if (!items.length) return null
  return <section className="content-section"><div className="section-heading"><div><p className="eyebrow">{subtitle || 'HANDPICKED FOR YOUR NEXT NIGHT IN'}</p><h2>{title}</h2></div>{action}</div><div className="movie-row">{items.slice(0,12).map(m=><MovieCard key={m.id} movie={m} onOpen={onOpen}/>)}</div></section>
}

export default function App() {
  const [trending,setTrending]=useState<Movie[]>([]), [popular,setPopular]=useState<Movie[]>([]), [top,setTop]=useState<Movie[]>([]), [catalogMovies,setCatalogMovies]=useState<Movie[]>([])
  const [query,setQuery]=useState(''), [results,setResults]=useState<Movie[]>([]), [searching,setSearching]=useState(false), [searched,setSearched]=useState(false)
  const [genre,setGenre]=useState('All Movies'), [discover,setDiscover]=useState<Movie[]>([])
  const [selected,setSelected]=useState<Movie|null>(null), [similar,setSimilar]=useState<Movie[]>([]), [detailLoading,setDetailLoading]=useState(false)
  const [prefs,setPrefs]=useState<string[]>([]), [liked,setLiked]=useState<string[]>([]), [personal,setPersonal]=useState<Movie[]>([]), [personalLoading,setPersonalLoading]=useState(false)
  const [error,setError]=useState(''), [notice,setNotice]=useState(''), [apiStatus,setApiStatus]=useState<{tmdb_enabled:boolean,catalog_size:number}|null>(null)
  const [mobileMenu,setMobileMenu]=useState(false)
  useEffect(()=>{ Promise.all([collection('trending'),collection('popular'),collection('top-rated'),filterMovies('All Movies'),health()]).then(([a,b,c,d,h])=>{setTrending(a.items);setPopular(b.items);setTop(c.items);setDiscover(d.items);setCatalogMovies(d.items);setApiStatus(h)}).catch(e=>setError(e.message)) },[])
  async function runSearch(e?:FormEvent) {
    e?.preventDefault(); const q=query.trim()
    if(!q){setSearched(false);setResults([]);return}
    setSearching(true);setSearched(true);setError('')
    try{const data=await searchMovies(q,genre);setResults(data.items)}catch(e){setError(e instanceof Error?e.message:'Search failed')}finally{setSearching(false)}
  }
  async function openMovie(movie:Movie) {
    setSelected(movie);setSimilar([]);setDetailLoading(true);setError('')
    try {
      const detail=await getMovie(movie.id);setSelected({...movie,...detail})
      try {const rec=await similarMovies(movie.id);setSimilar(rec.items)} catch { /* TMDB-only titles may not exist in local ML catalog */ }
    } catch(e) {setError(e instanceof Error?e.message:'Could not load movie details')}
    finally {setDetailLoading(false)}
  }
  async function chooseGenre(g:string) {
    setGenre(g);setError('')
    try{const data=await filterMovies(g);setDiscover(data.items);if(searched && query.trim()){const matches=await searchMovies(query.trim(),g);setResults(matches.items)}}catch(e){setError(e instanceof Error?e.message:'Could not filter movies')}
  }
  async function getPersonalized() {
    if(!prefs.length&&!liked.length){setNotice('Choose at least one genre or liked movie first.');return}
    setNotice('');setPersonalLoading(true)
    try{const data=await personalized(prefs,liked);setPersonal(data.items)}catch(e){setNotice(e instanceof Error?e.message:'Could not generate suggestions')}finally{setPersonalLoading(false)}
  }
  return <div className="app-shell">
    <div className="ambient-bg" aria-hidden="true"/>
    <header className="navbar"><a href="#home" className="brand"><span className="brand-mark"><Clapperboard size={20}/></span><span>Cine<span>Glow</span></span></a>
      <nav className={mobileMenu?'nav-links open':'nav-links'}><a href="#home" onClick={()=>setMobileMenu(false)}>Home</a><a href="#discover" onClick={()=>setMobileMenu(false)}>Discover</a><a href="#personalized" onClick={()=>setMobileMenu(false)}>For you</a></nav>
      <form className="nav-search" onSubmit={runSearch}><Search size={17}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Find a movie..." aria-label="Search movies"/>{query&&<button type="button" onClick={()=>{setQuery('');setSearched(false);setResults([])}} aria-label="Clear search"><X size={15}/></button>}<button className="search-submit" type="submit" aria-label="Submit search"><ArrowRight size={16}/></button></form>
      <button className="menu-toggle" onClick={()=>setMobileMenu(!mobileMenu)} aria-label="Toggle navigation">{mobileMenu?<X/>:<Menu/>}</button>
    </header>
    {error&&<div className="toast error-toast"><span>{error}</span><button onClick={()=>setError('')}><X size={16}/></button></div>}
    <main>
      <section className="hero" id="home"><div className="hero-copy"><div className="pill"><Sparkles size={14}/> YOUR NEXT FAVORITE STARTS HERE</div>
        <h1>Movies that<br/> <span>get your vibe.</span></h1>
        <p className="hero-description">A little movie magic, a lot less scrolling. Discover stories that match your mood, your taste, and your kind of night.</p>
        <div className="hero-actions"><a className="primary-btn" href="#discover">Explore movies <ArrowRight size={17}/></a><a className="secondary-btn" href="#personalized"><WandSparkles size={17}/> Make it personal</a></div>
        <div className="hero-footnote"><span className="avatar-stack"><i>✦</i><i>▶</i><i>★</i></span><span>Less searching. More watching.</span></div>
      </div>
      <div className="hero-art"><div className="art-glow"/><div className="art-orbit orbit-one"/><div className="art-orbit orbit-two"/><div className="feature-poster poster-back"><img src={poster(trending[2]||{title:'Interstellar'})} alt="Featured movie artwork"/></div><div className="feature-poster poster-front"><img src={poster(trending[0]||{title:'Inception'})} alt="Featured movie artwork"/><div className="poster-caption"><span>TONIGHT'S MOOD</span><strong>{trending[0]?.title||'A little cinematic magic'}</strong><span className="poster-caption-rating"><Star size={12} fill="currentColor"/> Made for your watchlist</span></div></div><div className="floating-chip chip-top"><Sparkles size={15}/> Your taste, decoded</div><div className="floating-chip chip-bottom"><span className="chip-dot"/> Smart picks, less scrolling</div></div>
      </section>
      <div className="trust-strip"><div><Sparkles size={18}/><span>Thoughtful recommendations</span></div><div><Compass size={18}/><span>Explore every genre</span></div><div><Film size={18}/><span>Find your next obsession</span></div></div>
      {searched && (
        <section className="content-section search-results-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR SEARCH</p>
              <h2>Results for “{query}”</h2>
              <p className="muted">{results.length} movie{results.length === 1 ? '' : 's'} found{genre !== 'All Movies' ? ` in ${genre}` : ''}</p>
            </div>
            <button className="text-btn" onClick={() => { setSearched(false); setResults([]) }}><X size={16} /> Clear results</button>
          </div>
          {searching ? (
            <div className="loading-state"><LoaderCircle className="spin" /> Searching movies…</div>
          ) : results.length ? (
            <div className="movie-grid">{results.map(m => <MovieCard key={m.id} movie={m} onOpen={openMovie} />)}</div>
          ) : (
            <div className="empty-state"><Search size={28} /><h3>No movies found</h3><p>Try another title or check the spelling.</p></div>
          )}
        </section>
      )}
      {!searched && (
        <>
          <Section title={apiStatus?.tmdb_enabled ? "Trending right now" : "Start with these"} subtitle={apiStatus?.tmdb_enabled ? 'POPULAR THIS WEEK · TMDB' : 'A FEW GOOD PLACES TO START'} items={trending} onOpen={openMovie} />
          <Section title="Crowd favourites" subtitle="MOVIES WORTH THE HYPE" items={popular} onOpen={openMovie} />
          <Section title={apiStatus?.tmdb_enabled ? "Critically loved" : "More to explore"} subtitle={apiStatus?.tmdb_enabled ? "THE HIGHLY RATED SHELF" : "CURATED STARTER PICKS"} items={top} onOpen={openMovie} />
        </>
      )}
      <section className="discover-section content-section" id="discover"><div className="section-heading"><div><p className="eyebrow">FIND YOUR GENRE</p><h2>What are we in the mood for?</h2><p className="muted">Pick a lane. We’ll bring the stories.</p></div><div className="discover-icon"><SlidersHorizontal size={19}/></div></div>
        <div className="genre-chips"><button className={genre==='All Movies'?'active':''} onClick={()=>chooseGenre('All Movies')}>All movies</button>{genres.map(g=><button key={g} className={genre===g?'active':''} onClick={()=>chooseGenre(g)}>{g}</button>)}</div>
        {discover.length?<div className="movie-grid">{discover.slice(0,12).map(m=><MovieCard key={m.id} movie={m} onOpen={openMovie}/>)}</div>:<div className="empty-state"><Film size={28}/><h3>No movies in this category yet</h3><p>Try another genre or reset to all movies.</p><button className="secondary-btn" onClick={()=>chooseGenre('All Movies')}>Show all movies</button></div>}
      </section>
      <section className="personal-section" id="personalized"><div className="personal-copy"><div className="pill dark-pill"><WandSparkles size={14}/> YOUR PERSONAL MOVIE MATCH</div><h2>A little more <span>you.</span></h2><p>Tell us what you love. Our content-based recommendation engine uses movie genres, story descriptions, and keywords to find your next watch.</p><div className="personal-note"><Sparkles size={17}/><span>Powered by TF-IDF + cosine similarity, not random picks.</span></div></div>
        <div className="preference-panel"><div className="panel-heading"><div><span className="step-label">01 / YOUR TASTE</span><h3>Choose your genres</h3></div><span className="panel-spark"><Heart size={18}/></span></div><div className="genre-chips preference-chips">{genres.map(g=><button key={g} className={prefs.includes(g)?'active':''} onClick={()=>setPrefs(old=>old.includes(g)?old.filter(x=>x!==g):[...old,g])}>{prefs.includes(g)&&'✓ '}{g}</button>)}</div>
          <div className="panel-heading liked-heading"><div><span className="step-label">02 / OPTIONAL</span><h3>Pick movies you like</h3></div><span className="liked-count">{liked.length} selected</span></div><div className="liked-movies">{catalogMovies.slice(0,12).map(m=><button key={m.id} className={liked.includes(String(m.id))?'liked':''} onClick={()=>setLiked(old=>old.includes(String(m.id))?old.filter(x=>x!==String(m.id)):[...old,String(m.id)])}><img src={poster(m)} alt=""/><span>{m.title}</span>{liked.includes(String(m.id))&&<i>✓</i>}</button>)}</div>
          <button className="primary-btn full-btn" onClick={getPersonalized} disabled={personalLoading}>{personalLoading?<LoaderCircle className="spin" size={17}/>:<Sparkles size={17}/>} {personalLoading?'Finding your matches':'Find my movies'} <ArrowRight size={16}/></button>{notice&&<p className="inline-notice">{notice}</p>}
        </div>
      </section>
      {personal.length>0&&<section className="content-section personal-results"><div className="section-heading"><div><p className="eyebrow">MADE AROUND YOUR TASTE</p><h2>Your next favourites</h2></div><button className="text-btn" onClick={()=>{setPersonal([]);setNotice('')}}><RotateCcw size={15}/> Reset</button></div><div className="movie-grid">{personal.map(m=><MovieCard key={m.id} movie={m} onOpen={openMovie}/>)}</div></section>}
    </main>
    <footer><a href="#home" className="brand"><span className="brand-mark"><Clapperboard size={18}/></span><span>Cine<span>Glow</span></span></a><p>Made for movie nights and curious minds. Movie imagery and metadata are provided by their respective rights holders. This product uses TMDB imagery/API where available and is not endorsed or certified by TMDB.</p><span className="footer-right">Discover a little wonder. ✦</span></footer>
    <AnimatePresence>{selected&&<motion.div className="modal-backdrop" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} onMouseDown={e=>{if(e.target===e.currentTarget)setSelected(null)}}><motion.div className="movie-modal" role="dialog" aria-modal="true" aria-label={`${selected.title} details`} initial={{opacity:0,y:18,scale:.98}} animate={{opacity:1,y:0,scale:1}} exit={{opacity:0,y:12,scale:.98}} transition={{duration:.2}}>
      <button className="modal-close" onClick={()=>setSelected(null)} aria-label="Close details"><X/></button><div className="modal-hero" style={{backgroundImage:`linear-gradient(90deg,rgba(26,17,43,.96),rgba(26,17,43,.65),rgba(26,17,43,.18)),url("${selected.backdrop_path||poster(selected)}")`}}><div className="modal-copy"><p className="eyebrow">MOVIE DETAILS</p><h2>{selected.title}</h2><div className="modal-facts">{year(selected)&&<span>{year(selected)}</span>}{rating(selected)&&<span><Star size={13} fill="currentColor"/> {rating(selected)}</span>}{selected.runtime&&<span>{selected.runtime} min</span>}</div><div className="modal-genres">{(selected.genre_names||selected.genres||[]).map(g=><span key={g}>{g}</span>)}</div></div></div><div className="modal-body"><h3>The story</h3><p>{selected.overview||'A synopsis is not available for this title.'}</p>{selected.source==='tmdb'&&<p className="attribution">Movie data provided by TMDB.</p>}
        <div className="recommendation-head"><div><p className="eyebrow">THE ML MATCHMAKER</p><h3>Because you picked this</h3></div><span className="ml-badge"><Sparkles size={13}/> TF-IDF</span></div>{detailLoading?<div className="loading-state"><LoaderCircle className="spin"/> Finding similar stories…</div>:similar.length?<div className="modal-recs">{similar.slice(0,5).map(m=><button key={m.id} onClick={()=>openMovie(m)}><img src={poster(m)} alt=""/><span><strong>{m.title}</strong><small>{m.recommendation_reason||'Similar movie themes'}</small></span><ArrowRight size={15}/></button>)}</div>:<p className="muted small">ML recommendations are available for movies in the included catalog. Configure TMDB to explore more titles, then choose a catalog movie for similarity matches.</p>}</div>
      </motion.div></motion.div>}</AnimatePresence>
  </div>
}
