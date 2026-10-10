import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { UserProvider } from './context/UserContext'
import { GlobalStateProvider } from './context/GlobalStateContext'
import { AuthProvider } from './context/AuthContext'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <UserProvider>
        <GlobalStateProvider>
          <App />
        </GlobalStateProvider>
      </UserProvider>
    </AuthProvider>
  </React.StrictMode>,
)
