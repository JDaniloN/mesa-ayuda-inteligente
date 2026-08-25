import { ChangeDetectionStrategy, Component } from '@angular/core';

import { ListadoSolicitudesComponent } from './solicitudes/listado-solicitudes.component';

@Component({
  imports: [ListadoSolicitudesComponent],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {}
