import { TestBed } from '@angular/core/testing';

import { ApiTokenService } from './api-token.service';

describe('ApiTokenService', () => {
  let service: ApiTokenService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ApiTokenService);
    localStorage.clear();
    sessionStorage.clear();
  });

  it('conserva el token únicamente durante la vida del servicio', () => {
    expect(service.establecer('  token-temporal  ')).toBe(true);

    expect(service.obtener()).toBe('token-temporal');
    expect(service.configurado()).toBe(true);
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);

    service.limpiar();
    expect(service.obtener()).toBe('');
  });

  it('rechaza un valor compuesto solo por espacios', () => {
    expect(service.establecer('   ')).toBe(false);
    expect(service.configurado()).toBe(false);
  });
});
