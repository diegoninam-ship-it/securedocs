export function Mensaje({ tipo, texto }: { tipo: 'error' | 'conflicto' | 'info'; texto: string }) {
  return <p className={`mensaje mensaje-${tipo}`}>{texto}</p>
}
