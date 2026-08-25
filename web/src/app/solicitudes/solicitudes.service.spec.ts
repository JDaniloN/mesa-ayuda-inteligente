import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { SolicitudesService } from './solicitudes.service';

describe('SolicitudesService', () => {
  let service: SolicitudesService;
  let controlador: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(SolicitudesService);
    controlador = TestBed.inject(HttpTestingController);
  });

  afterEach(() => controlador.verify());

  it('envía únicamente filtros diligenciados y conserva X-Request-ID', () => {
    let requestId = '';
    service
      .listar({
        area: ' Aplicaciones ',
        estado: '',
        prioridad: 'Alta',
        limite: 25,
      })
      .subscribe((resultado) => (requestId = resultado.requestId));

    const peticion = controlador.expectOne(
      (request) => request.url === '/api/solicitudes',
    );
    expect(peticion.request.params.get('area')).toBe('Aplicaciones');
    expect(peticion.request.params.get('prioridad')).toBe('Alta');
    expect(peticion.request.params.get('limite')).toBe('25');
    expect(peticion.request.params.has('estado')).toBe(false);

    peticion.flush([], {
      headers: { 'X-Request-ID': 'referencia-123' },
    });
    expect(requestId).toBe('referencia-123');
  });
});
