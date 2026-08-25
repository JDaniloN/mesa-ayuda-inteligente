import { HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Observable, of, throwError } from 'rxjs';

import { ApiTokenService } from '../core/api-token.service';
import {
  FiltrosSolicitudes,
  ResultadoSolicitudes,
} from './solicitud.model';
import { ListadoSolicitudesComponent } from './listado-solicitudes.component';
import { SolicitudesService } from './solicitudes.service';

class SolicitudesFalsas {
  llamadas = 0;
  respuesta: Observable<ResultadoSolicitudes> = of({
    solicitudes: [],
    requestId: 'request-vacio',
  });

  listar(_filtros: FiltrosSolicitudes): Observable<ResultadoSolicitudes> {
    this.llamadas += 1;
    return this.respuesta;
  }
}

describe('ListadoSolicitudesComponent', () => {
  let token: ApiTokenService;
  let servicio: SolicitudesFalsas;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListadoSolicitudesComponent],
      providers: [
        {
          provide: SolicitudesService,
          useClass: SolicitudesFalsas,
        },
      ],
    }).compileComponents();
    token = TestBed.inject(ApiTokenService);
    servicio = TestBed.inject(SolicitudesService) as unknown as SolicitudesFalsas;
  });

  it('no consulta mientras falta el token', () => {
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;

    componente.consultar();

    expect(servicio.llamadas).toBe(0);
    expect(componente.mensajeError()).toContain('Configure el token');
  });

  it('permite mostrar y volver a ocultar el token mientras se escribe', () => {
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;
    fixture.detectChanges();

    expect(
      (fixture.nativeElement.querySelector('#api-token') as HTMLInputElement).type,
    ).toBe('password');

    componente.alternarVisibilidadToken();
    fixture.detectChanges();
    expect(
      (fixture.nativeElement.querySelector('#api-token') as HTMLInputElement).type,
    ).toBe('text');
  });

  it('valida el token y consulta automáticamente al guardarlo', () => {
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;
    componente.tokenControl.setValue('demo-api-local');

    componente.guardarToken();

    expect(servicio.llamadas).toBe(1);
    expect(token.configurado()).toBe(true);
    expect(componente.tokenControl.value).toBe('');
    expect(componente.estadoAutenticacion()).toBe('autenticado');
  });

  it('impide que el formulario serialice el token en la URL', () => {
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;
    componente.tokenControl.setValue('demo-api-local');
    fixture.detectChanges();
    const formulario = fixture.nativeElement.querySelector(
      '.token-form',
    ) as HTMLFormElement;
    const evento = new Event('submit', { bubbles: true, cancelable: true });

    formulario.dispatchEvent(evento);

    expect(evento.defaultPrevented).toBe(true);
    expect(window.location.search).not.toContain('demo-api-local');
    expect(componente.estadoAutenticacion()).toBe('autenticado');
  });

  it('muestra el estado vacío como resultado válido', () => {
    token.establecer('token-demo');
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;

    componente.consultar();
    fixture.detectChanges();

    expect(servicio.llamadas).toBe(1);
    expect(componente.mensajeError()).toBe('');
    expect(componente.requestId()).toBe('request-vacio');
    expect(fixture.nativeElement.textContent).toContain(
      'No hay solicitudes que coincidan',
    );
  });

  it('elimina el token de memoria cuando la API responde 401', () => {
    token.establecer('token-rechazado');
    servicio.respuesta = throwError(
      () =>
        new HttpErrorResponse({
          status: 401,
          headers: new HttpHeaders({ 'X-Request-ID': 'request-401' }),
        }),
    );
    const fixture = TestBed.createComponent(ListadoSolicitudesComponent);
    const componente = fixture.componentInstance;

    componente.consultar();

    expect(token.configurado()).toBe(false);
    expect(componente.estadoAutenticacion()).toBe('rechazado');
    expect(componente.requestId()).toBe('request-401');
    expect(componente.mensajeError()).toContain('se eliminó de la memoria');
  });
});
