import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import './auth.css'
import App from './AppReal'

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
