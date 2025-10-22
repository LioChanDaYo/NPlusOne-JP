'use client'
import { useEffect, useState } from 'react'
const API = process.env.NEXT_PUBLIC_API || 'http://localhost:8000'


export default function Review(){
    const [cards, setCards] = useState<any[]>([])


    async function load(){
        const r = await fetch(`${API}/srs/due`)
        setCards(await r.json())
    }
    useEffect(()=>{ load() },[])


    async function grade(card_id:number, rating:number){
        await fetch(`${API}/srs/review`,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({card_id, rating, latency_ms:1000})})
        await load()
    }


    if(!cards.length) return <main><h2>Rien à réviser 🎉</h2><button onClick={load}>Rafraîchir</button></main>
    return (
        <main>
            <h2>Révision</h2>
            {cards.map(c=> (
                <div className="card" key={c.id}>
                    <div><b>{c.kind==='recog'?'Recognition:':'Retrieval:'}</b> {c.question}</div>
                    <div>Mot cible: <b>{c.lemma}</b></div>
                    <div className="row">
                        {[1,2,3,4].map(r=> <button key={r} onClick={()=>grade(c.id,r)}>{r}</button>)}
                    </div>
                </div>
            ))}
        </main>
    )
}