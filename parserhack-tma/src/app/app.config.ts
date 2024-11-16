import {ApplicationConfig, Injectable, provideZoneChangeDetection} from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import {
  HTTP_INTERCEPTORS,
  HttpEvent, HttpHandler,
  HttpHandlerFn, HttpInterceptor,
  HttpRequest,
  provideHttpClient,
  withInterceptors, withInterceptorsFromDi
} from '@angular/common/http';
import {Observable} from 'rxjs';
import {provideAnimations} from '@angular/platform-browser/animations';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<any>, handler: HttpHandler): Observable<HttpEvent<any>> {
    const token = 'ea2cf2f4d0406654a06d23eb9a8524e2d414e3fe';
    const update = {
      headers: request.headers.append('Authorization', `Token ${token}`)
    };
    const requestNew = request.clone(update);
    console.log("TEST");
    return handler.handle(requestNew);
  }
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(
      // DI-based interceptors must be explicitly enabled.
      withInterceptorsFromDi(),
    ),
    provideAnimations(),
    {provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true}
  ]
};

// export function authInterceptor(request: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> {
//   const token = 'ea2cf2f4d0406654a06d23eb9a8524e2d414e3fe';
//   const update = {
//     headers: request.headers.append('Authorization', `Token ${token}`)
//   };
//   const requestNew = request.clone(update);
//   console.log("TEST");
//   return next(requestNew);
// }
