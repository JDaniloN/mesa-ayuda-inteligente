import { DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  OnDestroy,
  signal,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { finalize, Subscription } from 'rxjs';

import { ApiTokenService } from '../core/api-token.service';
import { Solicitud } from './solicitud.model';
import { SolicitudesService } from './solicitudes.service';

type EstadoAutenticacion =
  | 'sin_token'
  | 'validando'
  | 'autenticado'
  | 'rechazado'
  | 'error';

@Component({
  selector: 'app-listado-solicitudes',
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './listado-solicitudes.component.html',
  styleUrl: './listado-solicitudes.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListadoSolicitudesComponent implements OnDestroy {
  private readonly apiToken = inject(ApiTokenService);
  private readonly solicitudesService = inject(SolicitudesService);
  private consultaActual?: Subscription;

  readonly tokenConfigurado = this.apiToken.configurado;
  readonly solicitudes = signal<Solicitud[]>([]);
  readonly cargando = signal(false);
  readonly consultado = signal(false);
  readonly mensajeError = signal('');
  readonly requestId = signal('');
  readonly mostrarToken = signal(false);
  readonly estadoAutenticacion = signal<EstadoAutenticacion>('sin_token');
  readonly textoAutenticacion = computed(() => {
    switch (this.estadoAutenticacion()) {
      case 'validando':
        return 'Validando acceso…';
      case 'autenticado':
        return 'Token autenticado por la API';
      case 'rechazado':
        return 'Token rechazado';
      case 'error':
        return 'No fue posible validar el token';
      default:
        return 'Sin autenticar';
    }
  });

  readonly tokenControl = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required],
  });

  readonly filtros = new FormGroup({
    area: new FormControl('', { nonNullable: true }),
    estado: new FormControl('', { nonNullable: true }),
    prioridad: new FormControl('', { nonNullable: true }),
    limite: new FormControl(50, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1), Validators.max(200)],
    }),
  });

  guardarToken(event?: Event): void {
    event?.preventDefault();
    if (this.tokenControl.invalid) {
      this.tokenControl.markAsTouched();
      this.mensajeError.set('Ingrese el token local de la API.');
      return;
    }
    const guardado = this.apiToken.establecer(this.tokenControl.value);
    this.tokenControl.reset('');
    this.mostrarToken.set(false);
    if (!guardado) {
      this.estadoAutenticacion.set('sin_token');
      this.mensajeError.set('El token no puede contener únicamente espacios.');
      return;
    }
    this.estadoAutenticacion.set('validando');
    this.mensajeError.set('');
    this.consultar(true);
  }

  alternarVisibilidadToken(): void {
    this.mostrarToken.update((visible) => !visible);
  }

  quitarToken(): void {
    this.apiToken.limpiar();
    this.estadoAutenticacion.set('sin_token');
    this.mostrarToken.set(false);
    this.consultaActual?.unsubscribe();
    this.solicitudes.set([]);
    this.consultado.set(false);
    this.requestId.set('');
    this.mensajeError.set('El token se eliminó de la memoria del navegador.');
  }

  consultar(validandoToken = false): void {
    if (!this.apiToken.configurado()) {
      this.estadoAutenticacion.set('sin_token');
      this.mensajeError.set('Configure el token antes de consultar la API.');
      return;
    }
    if (this.filtros.invalid) {
      this.filtros.markAllAsTouched();
      this.mensajeError.set('El límite debe estar entre 1 y 200.');
      return;
    }

    this.consultaActual?.unsubscribe();
    this.cargando.set(true);
    this.mensajeError.set('');
    this.requestId.set('');

    this.consultaActual = this.solicitudesService
      .listar(this.filtros.getRawValue())
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (resultado) => {
          this.estadoAutenticacion.set('autenticado');
          this.solicitudes.set(resultado.solicitudes);
          this.requestId.set(resultado.requestId);
          this.consultado.set(true);
        },
        error: (error: unknown) => {
          if (validandoToken && this.estadoAutenticacion() === 'validando') {
            this.estadoAutenticacion.set('error');
          }
          this.solicitudes.set([]);
          this.consultado.set(true);
          this.mensajeError.set(this.mensajePara(error));
        },
      });
  }

  limpiarFiltros(): void {
    this.filtros.reset({
      area: '',
      estado: '',
      prioridad: '',
      limite: 50,
    });
    if (this.apiToken.configurado()) {
      this.consultar();
    }
  }

  ngOnDestroy(): void {
    this.consultaActual?.unsubscribe();
    this.apiToken.limpiar();
  }

  private mensajePara(error: unknown): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'No fue posible consultar las solicitudes.';
    }
    this.requestId.set(error.headers.get('X-Request-ID') ?? '');
    if (error.status === 0) {
      this.estadoAutenticacion.set('error');
      return 'No fue posible conectar con la API. Confirme que está en ejecución.';
    }
    if (error.status === 401) {
      this.apiToken.limpiar();
      this.estadoAutenticacion.set('rechazado');
      return 'El token fue rechazado y se eliminó de la memoria. Ingréselo nuevamente.';
    }
    if (error.status === 503) {
      this.estadoAutenticacion.set('error');
      return 'La API no tiene API_TOKEN configurado.';
    }
    const mensajeApi = error.error?.error?.mensaje;
    return mensajeApi || `La API respondió con estado ${error.status}.`;
  }
}
