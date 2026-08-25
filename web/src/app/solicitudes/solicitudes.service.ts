import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import {
  FiltrosSolicitudes,
  ResultadoSolicitudes,
  Solicitud,
} from './solicitud.model';

@Injectable({ providedIn: 'root' })
export class SolicitudesService {
  private readonly http = inject(HttpClient);
  private readonly url = '/api/solicitudes';

  listar(filtros: FiltrosSolicitudes): Observable<ResultadoSolicitudes> {
    let params = new HttpParams().set('limite', filtros.limite);
    for (const [nombre, valor] of Object.entries({
      area: filtros.area,
      estado: filtros.estado,
      prioridad: filtros.prioridad,
    })) {
      const limpio = valor.trim();
      if (limpio) {
        params = params.set(nombre, limpio);
      }
    }

    return this.http
      .get<Solicitud[]>(this.url, {
        params,
        observe: 'response',
      })
      .pipe(
        map((response) => ({
          solicitudes: response.body ?? [],
          requestId: response.headers.get('X-Request-ID') ?? '',
        })),
      );
  }
}
