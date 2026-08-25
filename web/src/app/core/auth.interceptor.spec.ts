import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ApiTokenService } from './api-token.service';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let http: HttpClient;
  let controlador: HttpTestingController;
  let tokens: ApiTokenService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    controlador = TestBed.inject(HttpTestingController);
    tokens = TestBed.inject(ApiTokenService);
  });

  afterEach(() => controlador.verify());

  it('adjunta el Bearer únicamente a la API interna', () => {
    tokens.establecer('token-temporal');

    http.get('/api/solicitudes').subscribe();
    const peticion = controlador.expectOne('/api/solicitudes');

    expect(peticion.request.headers.get('Authorization')).toBe(
      'Bearer token-temporal',
    );
    peticion.flush([]);
  });

  it('no envía el token a una URL externa', () => {
    tokens.establecer('token-temporal');

    http.get('https://tercero.example/datos').subscribe();
    const peticion = controlador.expectOne('https://tercero.example/datos');

    expect(peticion.request.headers.has('Authorization')).toBe(false);
    peticion.flush({});
  });

  it('no crea la cabecera mientras no haya token', () => {
    http.get('/api/solicitudes').subscribe();
    const peticion = controlador.expectOne('/api/solicitudes');

    expect(peticion.request.headers.has('Authorization')).toBe(false);
    peticion.flush([]);
  });
});
