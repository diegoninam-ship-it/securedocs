import { useState } from 'react'
import { getSimulador, setSimulador } from '../api/client'

export function SimuladorPanel() {
  const inicial = getSimulador()
  const [ubicacion, setUbicacion] = useState(inicial.ubicacion)
  const [dispositivo, setDispositivo] = useState(inicial.dispositivo)

  function actualizar(nuevaUbicacion: string, nuevoDispositivo: string) {
    setUbicacion(nuevaUbicacion)
    setDispositivo(nuevoDispositivo)
    setSimulador(nuevaUbicacion, nuevoDispositivo)
  }

  return (
    <div className="simulador">
      <span className="simulador-titulo">Simulador de contexto (DEMO_MODE)</span>
      <label>
        Ubicación
        <input
          type="text"
          maxLength={2}
          value={ubicacion}
          onChange={(e) => actualizar(e.target.value.toUpperCase(), dispositivo)}
        />
      </label>
      <label>
        Dispositivo
        <select value={dispositivo} onChange={(e) => actualizar(ubicacion, e.target.value)}>
          <option value="CORPORATIVO">CORPORATIVO</option>
          <option value="PERSONAL">PERSONAL</option>
        </select>
      </label>
    </div>
  )
}
