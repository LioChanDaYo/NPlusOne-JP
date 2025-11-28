'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

const API = process.env.NEXT_PUBLIC_API || 'http://localhost:8000'

export default function Review(){
    const [queue, setQueue] = useState<any[]>([])
    const [revealed, setRevealed] = useState(false)
    const [loading, setLoading] = useState(true)

    // Charge les cartes au démarrage
    async function load(){
        setLoading(true)
        const r = await fetch(`${API}/srs/due`)
        const data = await r.json()
        setQueue(data)
        setLoading(false)
        setRevealed(false)
    }
    useEffect(()=>{ load() },[])

    // Envoi de la note et passage à la carte suivante
    async function grade(rating:number){
        const card = queue[0]
        await fetch(`${API}/srs/review`,{
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({card_id: card.id, rating, latency_ms: 2000}) // latency mockée pour l'instant
        })
        
        // On retire la carte faite de la file locale pour aller plus vite (optimistic UI)
        setQueue(prev => prev.slice(1))
        setRevealed(false)
    }

    if(loading) return <main>Chargement...</main>
    if(!queue.length) return (
        <main style={{textAlign:'center', marginTop:50}}>
            <h2>🎉 Terminé pour l'instant !</h2>
            <p>Reviens plus tard pour d'autres révisions.</p>
            <Link href="/"><button>Retour à l'accueil</button></Link>
        </main>
    )

    const card = queue[0]

    return (
        <main>
            <div style={{display:'flex', justifyContent:'space-between'}}>
                <h2>Révision ({queue.length})</h2>
                <Link href="/">Quitter</Link>
            </div>
            
            <div className="card" style={{minHeight: 200, display:'flex', flexDirection:'column', justifyContent:'center', alignItems:'center', textAlign:'center'}}>
                
                {/* --- RECTO --- */}
                <div style={{color:'#666', marginBottom:10}}>{card.question}</div>
                
                {/* On affiche la phrase. Si c'est du "Retrieval" (production), on pourrait cacher le mot ici plus tard */}
                <div style={{fontSize:'1.5rem', marginBottom:20}}>
                    {card.sentence_text}
                </div>

                {/* --- VERSO (Réponse) --- */}
                {revealed && (
                    <div style={{marginTop:20, borderTop:'1px solid #eee', paddingTop:20, width:'100%'}}>
                        <div style={{color:'green', fontWeight:'bold', fontSize:'1.2rem'}}>
                            {card.lemma}
                        </div>
                        <p>Notez votre mémoire :</p>
                        <div className="row" style={{justifyContent:'center', gap:10}}>
                            <button style={{backgroundColor:'#ffcccc'}} onClick={()=>grade(1)}>Oublié (1)</button>
                            <button style={{backgroundColor:'#fff5cc'}} onClick={()=>grade(2)}>Difficile (2)</button>
                            <button style={{backgroundColor:'#ccffcc'}} onClick={()=>grade(3)}>Bien (3)</button>
                            <button style={{backgroundColor:'#ccffff'}} onClick={()=>grade(4)}>Facile (4)</button>
                        </div>
                    </div>
                )}

                {/* Bouton pour retourner la carte */}
                {!revealed && (
                    <button style={{marginTop:20, width:'100%', padding:15, fontWeight:'bold'}} onClick={()=>setRevealed(true)}>
                        Afficher la réponse
                    </button>
                )}
            </div>
        </main>
    )
}