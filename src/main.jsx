import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Import providers
import { QueryClient, QueryClientProvider } from 'react-query'
import { AuthProvider } from './context/AuthContext'
import { UserProvider } from './context/UserContext'
import { GlobalStateProvider } from './context/GlobalStateContext'

const queryClient = new QueryClient()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <UserProvider>
          <GlobalStateProvider>
            <App />
          </GlobalStateProvider>
        </UserProvider>
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
)
