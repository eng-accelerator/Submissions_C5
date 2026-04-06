import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Landing from './pages/Landing'
import Chat from './pages/Chat'
import Upload from './pages/Upload'
import Health from './pages/Health'
import Admin from './pages/Admin'
import BlogDetail from './pages/BlogDetail'
import Showcase from './pages/Showcase'
import Plan from './pages/Plan'
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/health" element={<Health />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/blog/:id" element={<BlogDetail />} />
        <Route path="/showcase" element={<Showcase />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}
