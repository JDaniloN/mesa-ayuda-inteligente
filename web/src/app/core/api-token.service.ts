import { computed, Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiTokenService {
  private readonly valor = signal('');

  readonly configurado = computed(() => this.valor().length > 0);

  establecer(token: string): boolean {
    const limpio = token.trim();
    this.valor.set(limpio);
    return limpio.length > 0;
  }

  obtener(): string {
    return this.valor();
  }

  limpiar(): void {
    this.valor.set('');
  }
}
