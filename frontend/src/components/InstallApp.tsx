import { useEffect, useState } from 'react'

type InstallPrompt = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: string }> }

function installed(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches
}

/** Offers to add CareerPath to the phone's home screen. Hidden when the browser can't, or it is already installed. */
export function InstallApp({ className = '' }: { className?: string }) {
  const [prompt, setPrompt] = useState<InstallPrompt | null>(null)
  const [done, setDone] = useState(installed)
  const apple = /iphone|ipad|ipod/i.test(navigator.userAgent)

  useEffect(() => {
    const offer = (event: Event) => {
      event.preventDefault()
      setPrompt(event as InstallPrompt)
    }
    const finished = () => setDone(true)
    window.addEventListener('beforeinstallprompt', offer)
    window.addEventListener('appinstalled', finished)
    return () => {
      window.removeEventListener('beforeinstallprompt', offer)
      window.removeEventListener('appinstalled', finished)
    }
  }, [])

  if (done) return null
  if (prompt) {
    return (
      <button
        type="button" className={`btn btn-outline ${className}`}
        onClick={async () => {
          await prompt.prompt()
          if ((await prompt.userChoice).outcome === 'accepted') setDone(true)
          setPrompt(null)
        }}
      >
        📲 Install the CareerPath app
      </button>
    )
  }
  if (apple) return <p className={`text-sm ${className}`}>📲 To install: tap Share, then “Add to Home Screen”.</p>
  return null
}
