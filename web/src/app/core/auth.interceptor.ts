import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { ApiTokenService } from './api-token.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const token = inject(ApiTokenService).obtener();
  const esApiInterna = request.url.startsWith('/api/');

  if (!token || !esApiInterna) {
    return next(request);
  }

  return next(
    request.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    }),
  );
};
