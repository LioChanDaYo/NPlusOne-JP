'use client'
import Link from 'next/link'
export default function Home(){
    return (
    <main>
        <h1>N+1 Japanese</h1>
        <p>Prototype: ajoute un mot, choisis des phrases, révise avec FSRS.</p>
        <div className="row">
            <Link href="/suggest"><button>Ajouter un mot → Choisir phrases</button></Link>
            <Link href="/review"><button>Réviser aujourd'hui</button></Link>
        </div>
    </main>
    )
}