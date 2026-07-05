import React, { useState } from 'react'
import axios from 'axios'

export default function App() {
  const [folderPath, setFolderPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [readme, setReadme] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    if (!folderPath.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('http://localhost:8001/generate-readme', { folder_path: folderPath })
      setReadme(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    }
    setLoading(false)
  }

  const downloadReadme = () => {
    if (!readme) return
    const blob = new Blob([readme.readme_markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'README.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">AI README Generator</h1>

      <div className="flex gap-2 mb-6">
        <input value={folderPath} onChange={e => setFolderPath(e.target.value)}
          placeholder="Enter project folder path (e.g. /Users/rudra/Documents/projects-github/...)"
          className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400" />
        <button onClick={handleGenerate} disabled={!folderPath || loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors whitespace-nowrap">
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </div>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-4">{error}</div>}

      {readme && <>
        <div className="flex gap-2 mb-4">
          <button onClick={downloadReadme} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Download README.md</button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {readme.badges?.length > 0 && <div className="bg-white p-4 rounded-lg shadow col-span-full">
            <div className="flex gap-2 flex-wrap">{readme.badges.map((b, i) => <span key={i} className="text-sm" dangerouslySetInnerHTML={{__html: b}} />)}</div>
          </div>}

          {readme.installation_steps?.length > 0 && <div className="bg-white p-4 rounded-lg shadow lg:col-span-2">
            <h3 className="font-semibold text-gray-700 mb-2">Installation</h3>
            <ol className="list-decimal list-inside space-y-1 text-gray-600">{readme.installation_steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
          </div>}

          {readme.license_suggestion && <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold text-gray-700 mb-2">License</h3>
            <p className="text-gray-600">{readme.license_suggestion}</p>
          </div>}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="font-semibold text-gray-700 mb-4">Preview</h3>
          <div className="prose max-w-none">
            {readme.readme_markdown.split('\n').map((line, i) => {
              if (line.startsWith('# ')) return <h1 key={i} className="text-3xl font-bold mt-4 mb-2">{line.slice(2)}</h1>
              if (line.startsWith('## ')) return <h2 key={i} className="text-2xl font-bold mt-4 mb-2">{line.slice(3)}</h2>
              if (line.startsWith('### ')) return <h3 key={i} className="text-xl font-bold mt-3 mb-1">{line.slice(4)}</h3>
              if (line.startsWith('- ')) return <li key={i} className="ml-4 text-gray-600">{line.slice(2)}</li>
              if (line.startsWith('```')) return <pre key={i} className="bg-gray-100 p-3 rounded my-2 overflow-x-auto"><code>{line.slice(3)}</code></pre>
              if (line.trim()) return <p key={i} className="text-gray-600 my-1">{line}</p>
              return <br key={i} />
            })}
          </div>
        </div>
      </>}
    </div>
  )
}
