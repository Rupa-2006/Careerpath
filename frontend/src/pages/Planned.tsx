import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="py-12 text-center">
      <h1 className="text-3xl">Page not found</h1>
      <p className="mt-2 text-muted">Let's get you back on your path.</p>
      <Link to="/" className="btn btn-primary mt-6">Go home</Link>
    </div>
  )
}
