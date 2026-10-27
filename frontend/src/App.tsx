import { Routes, Route } from 'react-router-dom'
import { Dashboard } from './components/Dashboard'
import { ScenarioTester } from './components/ScenarioTester'
import { JobDetails } from './components/JobDetails'
import { MapView } from './components/MapView'
import { Layout } from './components/Layout'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/scenarios" element={<ScenarioTester />} />
        <Route path="/jobs/:jobId" element={<JobDetails />} />
        <Route path="/map" element={<MapView />} />
      </Route>
    </Routes>
  )
}

export default App