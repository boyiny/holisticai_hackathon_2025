import { NavLink } from 'react-router-dom'

const nav = [
  { to: '/overview', label: 'Overview', icon: '📊' },
  { to: '/agents', label: 'Agents', icon: '🧑‍⚕️' },
  { to: '/workflow', label: 'Workflow', icon: '🔀' },
  { to: '/tools', label: 'Tools', icon: '🧰' },
  { to: '/analysis', label: 'Analysis', icon: '🔎' },
  { to: '/tests', label: 'Tests', icon: '✅' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-200 bg-white dark:bg-black dark:border-white/10 p-4 hidden md:block">
      <div className="font-display font-bold text-xl md:text-2xl mb-6">Longevity Agent Studio</div>
      <nav className="space-y-1">
        {nav.map(item => (
          <NavLink key={item.to} to={item.to} className={({isActive}) => 
            `flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 ${isActive ? 'bg-slate-100 dark:bg-white/10 font-medium' : ''}`
          }>
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
