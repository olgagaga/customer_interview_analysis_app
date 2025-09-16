import { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { api } from '../services/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

interface Interview {
  id: number
  title: string
  transcript: string
  analysis?: string | null
  created_at: string
}

export default function App() {
  const [productDescription, setProductDescription] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  function handleFileSelection(files: FileList | File[]) {
    const next = Array.from(files)
    const accepted = next.filter((f) => /\.(pdf|txt)$/i.test(f.name))
    if (accepted.length > 0) {
      setSelectedFiles((prev) => [...prev, ...accepted])
    }
  }

  async function fetchInterviews() {
    const { data } = await api.get<Interview[]>(`/api/v1/interviews`)
    setInterviews(data)
  }

  useEffect(() => {
    fetchInterviews()
  }, [])

  async function submitStart(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!selectedFiles || selectedFiles.length === 0) {
      setError('Please upload at least one transcript file (.pdf or .txt).')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      for (const file of selectedFiles) {
        formData.append('files', file)
      }
      if (productDescription.trim()) {
        // Use product_description for analysis; optional title stays separate
        formData.append('product_description', productDescription.trim())
        const compactTitle = productDescription.trim().slice(0, 120)
        formData.append('title', compactTitle)
      }

      await api.post(`/api/v1/interviews/upload`, formData)

      setSelectedFiles([])
      setProductDescription('')
      await fetchInterviews()
    } catch (err) {
      setError('Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const styles = {
    page: {
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #0a1733 0%, #0e254d 100%)',
      color: '#0b1220',
      padding: '2rem 1rem',
      fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
    } as React.CSSProperties,
    container: {
      maxWidth: 960,
      margin: '0 auto',
      display: 'grid',
      gap: '1.5rem',
    } as React.CSSProperties,
    card: {
      background: '#ffffff',
      borderRadius: 16,
      padding: '1.5rem',
      boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
    } as React.CSSProperties,
    headingWrap: {
      textAlign: 'center',
      color: '#e6eefc',
      marginBottom: '0.5rem',
    } as React.CSSProperties,
    heading: {
      margin: 0,
      fontSize: '1.75rem',
      fontWeight: 700,
      letterSpacing: 0.3,
    } as React.CSSProperties,
    subheading: {
      marginTop: 8,
      fontSize: '0.95rem',
      color: '#c9d6ef',
    } as React.CSSProperties,
    form: {
      display: 'grid',
      gap: '0.9rem',
    } as React.CSSProperties,
    label: {
      fontSize: '0.9rem',
      fontWeight: 600,
      color: '#0b1220',
    } as React.CSSProperties,
    textarea: {
      width: '100%',
      padding: '0.8rem 0.9rem',
      borderRadius: 10,
      border: '1px solid #d9e1f2',
      outline: 'none',
      resize: 'vertical',
      minHeight: 120,
      fontSize: '0.95rem',
      lineHeight: 1.5,
      background: '#f8fbff',
      boxSizing: 'border-box',
    } as React.CSSProperties,
    fileRow: {
      display: 'grid',
      gap: '0.4rem',
    } as React.CSSProperties,
    dropzone: {
      border: '2px dashed #bcd0f5',
      borderRadius: 12,
      padding: '1.25rem',
      background: '#f8fbff',
      textAlign: 'center',
      transition: 'border-color 120ms ease, background 120ms ease',
    } as React.CSSProperties,
    uploadBtn: {
      display: 'inline-block',
      marginTop: '0.6rem',
      padding: '0.6rem 0.9rem',
      fontSize: '0.95rem',
      fontWeight: 600,
      color: '#ffffff',
      background: 'linear-gradient(180deg, #1b4b8a 0%, #163a6a 100%)',
      border: 'none',
      borderRadius: 10,
      cursor: 'pointer',
    } as React.CSSProperties,
    fileInput: {
      width: '100%',
      padding: '0.7rem 0.9rem',
      background: '#f8fbff',
      border: '1px solid #d9e1f2',
      borderRadius: 10,
    } as React.CSSProperties,
    button: {
      padding: '0.85rem 1rem',
      fontSize: '1rem',
      fontWeight: 600,
      borderRadius: 12,
      border: 'none',
      color: '#ffffff',
      background: 'linear-gradient(180deg, #1b4b8a 0%, #163a6a 100%)',
      cursor: 'pointer',
    } as React.CSSProperties,
    error: {
      color: '#b42318',
      background: '#fee4e2',
      border: '1px solid #fecdca',
      padding: '0.6rem 0.75rem',
      borderRadius: 10,
      fontSize: '0.9rem',
    } as React.CSSProperties,
    listWrap: {
      display: 'grid',
      gap: '1rem',
    } as React.CSSProperties,
    listCard: {
      background: '#ffffff',
      borderRadius: 12,
      padding: '1rem',
      boxShadow: '0 6px 18px rgba(0,0,0,0.08)',
      border: '1px solid #ebf1ff',
    } as React.CSSProperties,
  }

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.headingWrap}>
          <h1 style={styles.heading}>Customer Interview Analysis</h1>
          <div style={styles.subheading}>Paste your product description and upload interview transcripts to get insights.</div>
        </div>

        <div style={styles.card}>
          <form onSubmit={submitStart} style={styles.form}>
            <div>
              <div style={styles.label}>Product description</div>
              <textarea
                placeholder="Paste product description (optional)"
                value={productDescription}
                onChange={(e) => setProductDescription(e.target.value)}
                style={styles.textarea}
              />
            </div>

            <div style={styles.fileRow}>
              <div style={styles.label}>Interview transcripts</div>
              <div
                style={{
                  ...styles.dropzone,
                  borderColor: isDragging ? '#7aa6ec' : (selectedFiles.length > 0 ? '#8db3ff' : '#bcd0f5'),
                  background: isDragging ? '#eef5ff' : '#f8fbff',
                }}
                onDragEnter={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(true)
                }}
                onDragOver={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(true)
                }}
                onDragLeave={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(false)
                }}
                onDrop={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setIsDragging(false)
                  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
                    handleFileSelection(e.dataTransfer.files)
                  }
                }}
              >
                <div style={{ color: '#163a6a', fontWeight: 600 }}>Drag & drop PDF or TXT files here</div>
                <div style={{ color: '#4b5563', fontSize: '0.9rem', marginTop: 4 }}>or</div>
                <button
                  type="button"
                  style={styles.uploadBtn}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Choose files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.txt"
                  onChange={(e) => handleFileSelection(e.target.files || [])}
                  style={{ display: 'none' }}
                />
              </div>
              {selectedFiles.length > 0 && (
                <div style={{ fontSize: '0.85rem', color: '#334155' }}>
                  {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected
                </div>
              )}
            </div>

            {error && <div style={styles.error}>{error}</div>}

            <div>
              <button disabled={loading} type="submit" style={styles.button}>
                {loading ? 'Analyzing…' : 'Analyze interviews'}
              </button>
            </div>
          </form>
        </div>

        <div style={{ color: '#e6eefc', marginTop: '0.25rem', fontSize: '0.95rem' }}>Recent analyses</div>
        <div style={styles.listWrap}>
          {interviews.map((i) => (
            <div key={i.id} style={styles.listCard}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <h3 style={{ margin: 0 }}>{i.title}</h3>
                <small>{new Date(i.created_at).toLocaleString()}</small>
              </div>
              <details style={{ marginTop: '0.5rem' }}>
                <summary>Transcript</summary>
                <pre style={{ whiteSpace: 'pre-wrap' }}>{i.transcript}</pre>
              </details>
              {i.analysis && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Analysis</strong>
                  <pre style={{ whiteSpace: 'pre-wrap' }}>{i.analysis}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 