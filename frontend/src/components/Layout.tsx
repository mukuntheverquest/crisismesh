import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, FlaskConical, MapPin, History, AlertTriangle } from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/scenarios', label: 'Scenarios', icon: FlaskConical },
  { path: '/map', label: 'Map View', icon: MapPin },
  { path: '/history', label: 'Job History', icon: History },
  { path: '/alerts', label: 'Active Alerts', icon: AlertTriangle },
]

export function Layout() {
  const location = useLocation()
  
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform transition-transform duration-200 lg:translate-x-0">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 p-6 border-b border-slate-200">
            <div className="w-10 h-10 rounded-xl bg-crisis-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">CrisisMesh</h1>
              <p className="text-xs text-slate-500">Disaster Management System</p>
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-crisis-50 text-crisis-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                )}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {item.label}
              </NavLink>
            ))}
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-slate-200">
            <div className="text-xs text-slate-500 text-center">
              Open Agent Hackathon 2026 - Track 1
            </div>
          </div>
        </div>
      </aside>
      
      {/* Main Content */}
      <main className="lg:ml-64 min-h-screen">
        <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
          <div className="flex items-center justify-between px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900 capitalize">
              {navItems.find(n => n.path === location.pathname)?.label || 'Dashboard'}
            </h2>
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-500 hidden sm:block">
                SAMPLE_MODE: ACTIVE
              </span>
              <div className="w-2 h-2 rounded-full bg-crisis-500 animate-pulse" title="System Online" />
            </div>
          </div>
        </header>
        
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}