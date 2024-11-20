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
import {AuthInterceptor} from './interceptors/auth.interceptor';

declare var token: string;

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
