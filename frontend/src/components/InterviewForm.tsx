import { useState } from 'react'

export function InterviewForm({ onSubmit }: { onSubmit: (title: string, transcript: string) => void }) {
  const [title, setTitle] = useState('')
  const [transcript, setTranscript] = useState('')

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit(title, transcript)
        setTitle('')
        setTranscript('')
      }}
      style={{ display: 'grid', gap: '0.75rem' }}
    >
      <input
        type="text"
        placeholder="Interview title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        style={{ padding: '0.5rem', fontSize: '1rem' }}
      />
      <textarea
        placeholder="Paste transcript"
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        required
        rows={10}
        style={{ padding: '0.5rem', fontSize: '1rem', lineHeight: 1.4 }}
      />
      <button type="submit" style={{ padding: '0.6rem 1rem', fontSize: '1rem' }}>
        Analyze
      </button>
    </form>
  )
} 