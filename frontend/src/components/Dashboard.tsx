import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  Zap, 
  Brain,
  Network,
  ChevronRight,
  Play,
  ArrowRight,
  Database
} from 'lucide-react'
import { formatDate, getSeverityColor, getStatusColor } from '../lib/utils'

interface Job {
  job_id: string
  status: string
  trace_id?: string
  started_at: string
  completed_at?: string
  disaster_context?: any
}

interface Scenario {
  id: string
  name: string
  disaster_type: string
  severity: string
  failure_archetype: string
  description: string
  test_data: any
  expected_outcome: string
}

const SCENARIOS: Scenario[] = [
  {
    id: 'texas_flash_flood_2025',
    name: 'Central Texas Flash Flood (July 2025)',
    disaster_type: 'flash_flood',
    severity: 'critical',
    failure_archetype: 'Sleeping Supervisor & Manual Approval Bottleneck',
    description: 'Over 12 inches of overnight rain sent a 29-34 ft flood wall down the Guadalupe River. NWS issued warning at 1:14 AM but opt-in alert wasn\'t sent until 5:02 AM - nearly 4 hours later.',
    test_data: {},
    expected_outcome: 'Autonomous 180-second dead-man switch triggers evacuation alert bypassing manual supervisor sign-off'
  },
  {
    id: 'la_wildfires_2025',
    name: 'Los Angeles Wildfires (January 2025)',
    disaster_type: 'wildfire',
    severity: 'critical',
    failure_archetype: 'Polygon Target Miss & Single-Operator Overload',
    description: 'Only one OEM operator manually issuing alerts across three simultaneous wildfires. Zero electronic alerts to West Altadena until 3:30-6:00 AM.',
    test_data: {},
    expected_outcome: 'Deterministic polygon guardrail blocks unbounded county-wide blasts; world model auto-expands evacuation polygons downwind'
  },
  {
    id: 'valencia_dana_2024',
    name: 'Valencia DANA Flash Flood (October 2024)',
    disaster_type: 'flash_flood',
    severity: 'catastrophic',
    failure_archetype: 'Forecast-to-Governance Disconnect & Jurisdictional Stand-Down',
    description: 'AEMET issued Red Alert early Oct 29, but regional government didn\'t send ES-Alert until 20:11 when 200,000 residents already inundated.',
    test_data: {},
    expected_outcome: 'Pre-authorized cross-jurisdictional SOP engine auto-generates joint mobilization orders from verified Red Alert'
  },
  {
    id: 'nepal_avalanche_2026',
    name: 'Nepal Bhote Koshi Rock-Ice Avalanche (August 2026)',
    disaster_type: 'rock_ice_avalanche',
    severity: 'catastrophic',
    failure_archetype: 'Sensor Destruction & Single-Modality Blindness',
    description: '5,200m Langtang rock-ice collapse sent 160 km/h debris surge. River gauges destroyed within 7 minutes.',
    test_data: {},
    expected_outcome: 'Multi-modal telemetry loss inference treats correlated sensor drop-off + seismic tremor as high-confidence hazard signal'
  },
  {
    id: 'nepal_floods_2024',
    name: 'Nepal Multi-Agency Registry Divergence (August 2024)',
    disaster_type: 'flash_flood',
    severity: 'high',
    failure_archetype: 'Manual PDF-to-CSV Nightmares & Multi-Agency Registry Divergence',
    description: 'Three incompatible rescued figures across competing portals. Developer manually converted Nepali Army PDFs to CSVs.',
    test_data: {},
    expected_outcome: 'Automated multi-format ingestion parses Army/NDRRMA PDFs into Zetaris in <15s, CUDA sentence-transformers deduplicate registries'
  },
  {
    id: 'libya_derna_2023',
    name: 'Derna Dam Collapse / Storm Daniel (September 2023)',
    disaster_type: 'dam_failure',
    severity: 'catastrophic',
    failure_archetype: 'Contradictory Official Messaging & Lethal Curfew Traps',
    description: 'Authorities imposed stay-at-home curfew. Water Ministry reassured dams in "good condition" - then ordered evacuation 19 minutes after collapse.',
    test_data: {},
    expected_outcome: 'Contradiction detection blocks curfew/shelter-in-place inside dam-breach polygon, enforces high-ground evacuation routing'
  },
  {
    id: 'nepal_floods_2026_multilingual',
    name: 'Nepal Floods Multilingual Alert Failure (August 2026)',
    disaster_type: 'flash_flood',
    severity: 'high',
    failure_archetype: 'Unilingual Generic Boilerplate Alerts Ignoring Tourists & Minorities',
    description: 'Flood SMS only in Nepali along major international trekking route where 636 foreign nationals from 39 countries went missing.',
    test_data: {},
    expected_outcome: 'Hyper-localized multilingual synthesizer auto-generates cell-broadcast in 10+ languages with exact arrival countdowns, shelter GPS'
  },
  {
    id: 'hurricane_helene_2024',
    name: 'Hurricane Helene Telecom/Power Isolation (September 2024)',
    disaster_type: 'hurricane',
    severity: 'catastrophic',
    failure_archetype: 'Total Telecom, Power & Road/Port Isolation (Brain vs Limbs Collapse)',
    description: 'Helene wiped out commercial cellular across 11 NC counties (>150K isolated) while landslides blocked mountain roads to tower generators.',
    test_data: {},
    expected_outcome: 'Offline-first edge execution (SAMPLE_MODE) + access-viability rerouting auto-reroutes from ground trucks to heli/drone/shallow-draft boat'
  },
  {
    id: 'turkiye_earthquake_2023',
    name: 'Türkiye-Syria Earthquake Social Media Overload (February 2023)',
    disaster_type: 'earthquake',
    severity: 'catastrophic',
    failure_archetype: 'Unstructured Social Media Distress Overload & Geocoding Hallucinations',
    description: '1,824,000 tweets in 12 hours overwhelmed manual triage; ~4% geocoded pins in wrong city.',
    test_data: {},
    expected_outcome: 'Satellite-grounded distress verification via GPU NLP + Zetaris spatial join against Sentinel-1 SAR damage footprints'
  },
  {
    id: 'nepal_tunnel_2026',
    name: 'Nepal Hydropower Tunnel Entrapment (August 2026)',
    disaster_type: 'industrial_accident',
    severity: 'critical',
    failure_archetype: 'High-Tech Cloud Dashboards vs Specialized Field Equipment Mismatch',
    description: '~500 workers trapped in dark, flooded hydropower tunnels. Army searched with smartphone flashlights due to lack of subterranean breaching gear.',
    test_data: {},
    expected_outcome: 'Capability-matched asset/NGO dispatch indexes pre-accredited civil, engineering, drone assets in Zetaris'
  }
]

function ScenarioCard({ scenario }: { scenario: Scenario }) {
  return (
    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-crisis-300 transition-colors">
      <div className="flex items-center gap-2 mb-2">
        <span className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityColor(scenario.severity)}`}>
          {scenario.severity.toUpperCase()}
        </span>
        <span className="px-2 py-0.5 text-xs font-medium bg-slate-100 text-slate-600 rounded">
          {scenario.disaster_type.replace('_', ' ').toUpperCase()}
        </span>
      </div>
      <h4 className="font-medium text-slate-900 mb-1">{scenario.name}</h4>
      <p className="text-xs text-slate-500 mb-2">{scenario.failure_archetype}</p>
      <p className="text-xs text-slate-600 mb-3 line-clamp-2">{scenario.description}</p>
      <button className="w-full py-1.5 px-2 text-xs font-medium text-crisis-600 hover:text-crisis-700 flex items-center justify-center gap-1">
        View Details
        <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  )
}

function JobRow({ job }: { job: Job }) {
  const duration = job.completed_at 
    ? Math.round((new Date(job.completed_at).getTime() - new Date(job.started_at).getTime()) / 1000)
    : Math.round((Date.now() - new Date(job.started_at).getTime()) / 1000)
  
  return (
    <tr className="hover:bg-slate-50">
      <td className="px-4 py-3 font-mono text-sm text-slate-600">{job.job_id.slice(0, 12)}...</td>
      <td className="px-4 py-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
          {job.status}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-slate-600 capitalize">
        {job.disaster_context?.disaster_type?.replace('_', ' ') || 'Unknown'}
      </td>
      <td className="px-4 py-3 text-sm text-slate-600">{formatDate(job.started_at)}</td>
      <td className="px-4 py-3 text-sm font-mono text-slate-500">{duration}s</td>
      <td className="px-4 py-3">
        <NavLink 
          to={`/jobs/${job.job_id}`}
          className="text-sm text-crisis-600 hover:text-crisis-700 font-medium"
        >
          View
        </NavLink>
      </td>
    </tr>
  )
}

export function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([])
  
  useEffect(() => {
    const stored = localStorage.getItem('crisismesh_jobs')
    if (stored) {
      try {
        setJobs(JSON.parse(stored))
      } catch {
        setJobs([])
      }
    }
  }, [])
  
  const sponsorStats = [
    { label: 'Zetaris', metric: 'Data Federation', value: 'Active', icon: Database, color: 'blue' },
    { label: 'Meterless', metric: 'Observability', value: 'Active', icon: Brain, color: 'purple' },
    { label: 'NVIDIA', metric: 'GPU Acceleration', value: 'Active', icon: Zap, color: 'green' },
    { label: 'Cursor', metric: 'AI-Native Dev', value: 'Active', icon: Network, color: 'orange' },
  ]
  
  const systemMetrics = [
    { label: 'Active Alerts', value: '3', change: '+1', trend: 'up' },
    { label: 'Evacuations Ordered', value: '1,247', change: '+342', trend: 'up' },
    { label: 'Assets Deployed', value: '23', change: '+5', trend: 'up' },
    { label: 'Shelter Capacity', value: '87%', change: '-3%', trend: 'down' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">CrisisMesh Dashboard</h1>
          <p className="text-slate-500 mt-1">Multi-agent disaster management system - Open Agent Hackathon 2026</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-2 px-3 py-1 bg-crisis-100 text-crisis-700 rounded-full text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-crisis-500 animate-pulse" />
            SAMPLE_MODE ACTIVE
          </span>
        </div>
      </div>
      
      {/* Sponsor Tech Status */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {sponsorStats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="card p-5">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-xl bg-${stat.color}-100 text-${stat.color}-600 flex items-center justify-center`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">{stat.label}</p>
                  <p className="text-lg font-bold text-slate-900">{stat.metric}</p>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className={`text-sm font-medium ${stat.value === 'Active' ? 'text-safe-600' : 'text-slate-600'}`}>
                  {stat.value}
                </span>
                <span className="text-xs text-slate-400">Track 1</span>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* System Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {systemMetrics.map((metric) => (
          <div key={metric.label} className="card p-5">
            <p className="text-sm text-slate-500">{metric.label}</p>
            <p className="text-3xl font-bold text-slate-900 mt-1">{metric.value}</p>
            <div className="flex items-center gap-1 mt-2">
              <span className={`text-sm font-medium ${metric.trend === 'up' ? 'text-safe-600' : 'text-crisis-600'}`}>
                {metric.trend === 'up' ? '↑' : '↓'} {metric.change}
              </span>
              <span className="text-xs text-slate-400">vs last hour</span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Disaster Scenarios & Recent Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenarios */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-slate-900">Disaster Failure Archetypes</h2>
            <NavLink to="/scenarios" className="text-sm text-crisis-600 hover:text-crisis-700 font-medium flex items-center gap-1">
              View All
              <ChevronRight className="w-4 h-4" />
            </NavLink>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
            {SCENARIOS.slice(0, 6).map((scenario) => (
              <ScenarioCard key={scenario.id} scenario={scenario} />
            ))}
          </div>
        </div>
        
        {/* Recent Jobs */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-slate-900">Recent Jobs</h2>
            <NavLink to="/history" className="text-sm text-crisis-600 hover:text-crisis-700 font-medium flex items-center gap-1">
              View All
              <ChevronRight className="w-4 h-4" />
            </NavLink>
          </div>
          {jobs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    <th className="px-4 py-2">Job ID</th>
                    <th className="px-4 py-2">Status</th>
                    <th className="px-4 py-2">Disaster</th>
                    <th className="px-4 py-2">Started</th>
                    <th className="px-4 py-2">Duration</th>
                    <th className="px-4 py-2">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {jobs.slice(0, 5).map((job) => (
                    <JobRow key={job.job_id} job={job} />
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Play className="w-12 h-12 mx-auto mb-3 text-slate-300" />
              <p>No jobs yet. Run a scenario to get started.</p>
              <NavLink to="/scenarios" className="inline-block mt-3 text-crisis-600 hover:text-crisis-700 font-medium">
                Browse Scenarios
              </NavLink>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}