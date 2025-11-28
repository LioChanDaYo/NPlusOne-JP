'use client'
import { useState } from 'react'
import Link from 'next/link'

const API = process.env.NEXT_PUBLIC_API || 'http://localhost:8000'

export default function Suggest(){
    const [lemma, setLemma] = useState('')
    const [cands, setCands] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    async function addWord(){
        if(!lemma) return
        setLoading(true)
        setCands([]) // Reset liste précédente
        const r = await fetch(`${API}/words/add-word`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({lemma})
        })
        const data = await r.json(); 
        setCands(data.candidates||[])
        setLoading(false)
    }

    async function accept(sentence_id:number){
        // Appel API
        await fetch(`${API}/words/accept`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ lemma, sentence_id, accept: true })
        })
        // Feedback visuel : on retire la phrase de la liste
        setCands(prev => prev.filter(c => c.id !== sentence_id))
    }

    return (
        <main>
            <Link href="/">← Retour</Link>
            <h2>Ajouter un mot</h2>
            <div className="row" style={{marginBottom:20}}>
                <input 
                    value={lemma} 
                    onChange={e=>setLemma(e.target.value)} 
                    onKeyDown={e => e.key === 'Enter' && addWord()}
                    placeholder="ex: 猫 (chat)" 
                    style={{padding:10, fontSize:16}}
                />
                <button onClick={addWord} disabled={loading}>
                    {loading ? 'Recherche...' : 'Chercher des phrases'}
                </button>
            </div>

            {/* Zone de résultats */}
            <div>
                {cands.map(c=> (
                    <div className="card" key={c.id || c.text}>
                        <div style={{fontSize:'1.2rem', marginBottom:8}}>{c.text}</div>
                        <div style={{color:'#888', fontSize:'0.8rem', marginBottom:8}}>
                            Source: {c.source}
                        </div>
                        <button onClick={()=>accept(c.id)}>👍 Garder cette phrase</button>
                    </div>
                ))}
                
                {/* Message si recherche vide ou terminée */}
                {!loading && cands.length === 0 && lemma && (
                   <p style={{color:'#666'}}>Pas de résultats affichés (ou tout a été traité).</p>
                )}
            </div>
            
            {/* Raccourci vers la révision */}
            <div style={{marginTop:40, borderTop:'1px solid #eee', paddingTop:20}}>
                <Link href="/review"><button style={{width:'100%', padding:15}}>Aller réviser →</button></Link>
            </div>
        </main>
    )
}