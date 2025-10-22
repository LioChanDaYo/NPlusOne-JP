'use client'
import { useState } from 'react'


const API = process.env.NEXT_PUBLIC_API || 'http://localhost:8000'


export default function Suggest(){
    const [lemma, setLemma] = useState('')
    const [cands, setCands] = useState<any[]>([])


    async function addWord(){
        const r = await fetch(`${API}/words/add-word`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({lemma})
        })
        const data = await r.json(); setCands(data.candidates||[])
    }


    async function accept(sentence_id:number, accept=true){
        await fetch(`${API}/words/accept`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ lemma, sentence_id, accept })
        })
        alert('ok — cartes créées')
    }


    return (
        <main>
            <h2>Ajouter un mot</h2>
            <div className="row">
                <input value={lemma} onChange={e=>setLemma(e.target.value)} placeholder="ex: 美味しい" />
                <button onClick={addWord}>Proposer des phrases</button>
            </div>
            <div>
                {cands.map(c=> (
                    <div className="card" key={c.id}>
                        <div>{c.text}</div>
                        <small>{c.source} · {c.source_id}</small><br/>
                        <button onClick={()=>accept(c.id,true)}>👍 Garder</button>
                    </div>
                ))}
            </div>
        </main>
    )
}