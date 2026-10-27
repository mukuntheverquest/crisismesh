import { useState, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, LayerGroup, Polyline } from 'react-leaflet'
import { MapPin, AlertTriangle, Users, Shield, Home, Truck, Zap } from 'lucide-react'
import L from 'leaflet'

// Fix marker icon defaults
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Sample disaster data for map visualization
const sampleAlerts = [
  { id: 'alert_1', lat: 30.0, lng: -99.5, type: 'flash_flood', severity: 'critical', name: 'Guadalupe River Flash Flood', radius: 15000 },
  { id: 'alert_2', lat: 34.1, lng: -118.3, type: 'wildfire', severity: 'critical', name: 'Eaton Fire', radius: 8000 },
  { id: 'alert_3', lat: 39.5, lng: -0.5, type: 'flash_flood', severity: 'critical', name: 'Valencia DANA Flood', radius: 25000 },
  { id: 'alert_4', lat: 27.9, lng: 85.8, type: 'rock_ice_avalanche', severity: 'critical', name: 'Bhote Koshi Avalanche', radius: 10000 },
]

const sampleEvacuationRoutes = [
  { id: 'route_1', name: 'High Ground Route - Kerr County', coordinates: [[30.1, -99.5], [30.2, -99.3], [30.3, -99.1]] as [number, number][], capacity: 500 },
  { id: 'route_2', name: 'Evacuation Corridor - Altadena', coordinates: [[34.2, -118.2], [34.3, -118.0], [34.4, -117.8]] as [number, number][], capacity: 1200 },
]

const sampleAssets = [
  { id: 'asset_1', lat: 30.1, lng: -99.3, type: 'helicopter', name: 'TX National Guard UH-60', status: 'deployed' },
  { id: 'asset_2', lat: 34.2, lng: -118.1, type: 'truck', name: 'LA County Fire Engine Strike Team', status: 'deployed' },
  { id: 'asset_3', lat: 39.6, lng: -0.4, type: 'truck', name: 'UME Heavy Rescue', status: 'staging' },
  { id: 'asset_4', lat: 28.0, lng: 85.5, type: 'helicopter', name: 'Nepal Army Mi-17', status: 'deployed' },
]

const sampleShelters = [
  { id: 'shelter_1', lat: 30.2, lng: -99.2, name: 'Kerrville High School', capacity: 300, occupied: 180 },
  { id: 'shelter_2', lat: 34.3, lng: -117.9, name: 'Pasadena Convention Center', capacity: 2000, occupied: 1450 },
  { id: 'shelter_3', lat: 39.6, lng: -0.3, name: 'Valencia Fairgrounds', capacity: 5000, occupied: 3200 },
]

type LayerId = 'all' | 'alerts' | 'evacuation' | 'assets' | 'shelters'

interface LayerConfig {
  id: LayerId
  label: string
  icon: React.ComponentType<{ className?: string }>
  color: string
}

const layers: LayerConfig[] = [
  { id: 'all', label: 'All Layers', icon: MapPin, color: 'slate' },
  { id: 'alerts', label: 'Active Alerts', icon: AlertTriangle, color: 'crisis' },
  { id: 'evacuation', label: 'Evacuation Routes', icon: Users, color: 'blue' },
  { id: 'assets', label: 'Deployed Assets', icon: Shield, color: 'safe' },
  { id: 'shelters', label: 'Shelters', icon: Home, color: 'alert' },
]

export function MapView() {
  const [selectedLayer, setSelectedLayer] = useState<LayerId>('all')
  const [mapCenter, setMapCenter] = useState<[number, number]>([30.0, -99.5])
  const [zoom, setZoom] = useState(5)
  const mapRef = useRef<any>(null)
  
  useEffect(() => {
    if (mapRef.current) {
      const map = mapRef.current.leafletElement
      map.on('moveend', () => {
        const center = map.getCenter()
        setMapCenter([center.lat, center.lng])
        setZoom(map.getZoom())
      })
    }
  }, [mapRef.current])

  return (
    <div className="h-[calc(100vh-200px)] min-h-[500px]">
      {/* Layer Controls */}
      <div className="mb-4 flex flex-wrap gap-2">
        {layers.map((layer) => (
          <button
            key={layer.id}
            onClick={() => setSelectedLayer(layer.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              selectedLayer === layer.id
                ? `bg-${layer.color}-600 text-white`
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <layer.icon className="w-4 h-4" />
            {layer.label}
          </button>
        ))}
      </div>
      
      {/* Map */}
      <div className="rounded-xl overflow-hidden border border-slate-200 shadow-sm">
        <MapContainer
          center={mapCenter}
          zoom={zoom}
          style={{ width: '100%', height: '100%' }}
          ref={mapRef}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {/* Alerts Layer */}
          {(selectedLayer === 'all' || selectedLayer === 'alerts') && (
            <LayerGroup>
              {sampleAlerts.map((alert) => (
                <Circle
                  key={alert.id}
                  center={[alert.lat, alert.lng]}
                  radius={alert.radius}
                  color={alert.severity === 'critical' ? '#ef4444' : '#f97316'}
                  fillColor={alert.severity === 'critical' ? '#ef4444' : '#f97316'}
                  fillOpacity={0.15}
                  weight={2}
                >
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle className="w-5 h-5 text-crisis-600" />
                        <strong>{alert.name}</strong>
                      </div>
                      <p className="text-sm text-slate-600">Type: {alert.type.replace('_', ' ')}</p>
                      <p className="text-sm text-slate-600">Severity: {alert.severity}</p>
                      <p className="text-xs text-slate-500">Radius: {(alert.radius/1000).toFixed(1)} km</p>
                    </div>
                  </Popup>
                </Circle>
              ))}
            </LayerGroup>
          )}
          
          {/* Evacuation Routes Layer */}
          {(selectedLayer === 'all' || selectedLayer === 'evacuation') && (
            <LayerGroup>
              {sampleEvacuationRoutes.map((route) => (
                <Polyline
                  key={route.id}
                  positions={route.coordinates}
                  color="#3b82f6"
                  weight={4}
                  opacity={0.8}
                  dashArray="10, 10"
                >
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <div className="flex items-center gap-2 mb-1">
                        <Users className="w-5 h-5 text-blue-600" />
                        <strong>{route.name}</strong>
                      </div>
                      <p className="text-sm text-slate-600">Capacity: {route.capacity} people</p>
                    </div>
                  </Popup>
                </Polyline>
              ))}
            </LayerGroup>
          )}
          
          {/* Assets Layer */}
          {(selectedLayer === 'all' || selectedLayer === 'assets') && (
            <LayerGroup>
              {sampleAssets.map((asset) => (
                <Marker
                  key={asset.id}
                  position={[asset.lat, asset.lng]}
                  icon={createAssetIcon(asset.type)}
                >
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <div className="flex items-center gap-2 mb-1">
                        {asset.type === 'helicopter' ? (
                          <Zap className="w-5 h-5 text-safe-600" />
                        ) : (
                          <Truck className="w-5 h-5 text-safe-600" />
                        )}
                        <strong>{asset.name}</strong>
                      </div>
                      <p className="text-sm text-slate-600">Type: {asset.type}</p>
                      <p className="text-sm text-slate-600 capitalize">Status: {asset.status}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </LayerGroup>
          )}
          
          {/* Shelters Layer */}
          {(selectedLayer === 'all' || selectedLayer === 'shelters') && (
            <LayerGroup>
              {sampleShelters.map((shelter) => (
                <Marker
                  key={shelter.id}
                  position={[shelter.lat, shelter.lng]}
                  icon={createShelterIcon()}
                >
                  <Popup>
                    <div className="p-2 min-w-[200px]">
                      <div className="flex items-center gap-2 mb-1">
                        <Home className="w-5 h-5 text-alert-600" />
                        <strong>{shelter.name}</strong>
                      </div>
                      <p className="text-sm text-slate-600">Capacity: {shelter.capacity}</p>
                      <p className="text-sm text-slate-600">Occupied: {shelter.occupied}</p>
                      <p className="text-sm text-slate-600">Available: {shelter.capacity - shelter.occupied}</p>
                      <div className="mt-2 h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-alert-500 transition-all" 
                          style={{ width: `${(shelter.occupied / shelter.capacity) * 100}%` }}
                        />
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </LayerGroup>
          )}
        </MapContainer>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
        <LegendItem color="#ef4444" label="Critical Alert Zone" />
        <LegendItem color="#f97316" label="High Alert Zone" />
        <LegendItem color="#3b82f6" label="Evacuation Route" dash />
        <LegendItem icon={<Zap className="w-4 h-4 text-safe-600" />} label="Air Asset" />
        <LegendItem icon={<Truck className="w-4 h-4 text-safe-600" />} label="Ground Asset" />
        <LegendItem icon={<Home className="w-4 h-4 text-alert-600" />} label="Shelter" />
      </div>
    </div>
  )
}

function createAssetIcon(type: string) {
  const iconUrl = type === 'helicopter' 
    ? 'https://cdn.jsdelivr.net/npm/@mdi/svg@7.2.96/svg/helicopter.svg'
    : 'https://cdn.jsdelivr.net/npm/@mdi/svg@7.2.96/svg/truck.svg'
  
  return L.icon({
    iconUrl,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  })
}

function createShelterIcon() {
  return L.icon({
    iconUrl: 'https://cdn.jsdelivr.net/npm/@mdi/svg@7.2.96/svg/home-outline.svg',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  })
}

function LegendItem({ color, label, dash, icon }: { color?: string; label: string; dash?: boolean; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      {icon ? (
        <span className="flex items-center">{icon}</span>
      ) : (
        <div 
          className="w-8 h-3 rounded" 
          style={{ 
            background: color,
            borderTop: dash ? '2px dashed white' : 'none',
            borderBottom: dash ? '2px dashed white' : 'none',
          }} 
        />
      )}
      <span>{label}</span>
    </div>
  )
}