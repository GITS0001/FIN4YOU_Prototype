import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { UserProvider } from './context/UserContext'
import { GlobalStateProvider } from './context/GlobalStateContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <UserProvider>
      <GlobalStateProvider>
        <App />
      </GlobalStateProvider>
    </UserProvider>
  </React.StrictMode>,
)
