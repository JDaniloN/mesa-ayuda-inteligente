export type EstadoSolicitud = 'Abierto';
export type PrioridadSolicitud = 'Crítica' | 'Alta' | 'Media' | 'Baja';
export type OrigenClasificacion = 'proveedor' | 'degradado';

export interface Solicitud {
  id: string;
  asunto: string;
  descripcion: string;
  area: string;
  solicitante: string;
  canal: string;
  estado: EstadoSolicitud;
  fecha_creacion: string;
  categoria: string;
  prioridad: PrioridadSolicitud;
  origen_clasificacion: OrigenClasificacion;
}

export interface FiltrosSolicitudes {
  area: string;
  estado: string;
  prioridad: string;
  limite: number;
}

export interface ResultadoSolicitudes {
  solicitudes: Solicitud[];
  requestId: string;
}
