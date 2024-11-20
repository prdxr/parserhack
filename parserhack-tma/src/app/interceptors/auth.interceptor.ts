import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler, HttpHeaders,
  HttpInterceptor,
  HttpInterceptorFn,
  HttpRequest
} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {catchError, Observable, ObservableInput, of, throwError} from 'rxjs';
import {AuthService} from '../services/auth.service';

// export const authInterceptor: HttpInterceptorFn = (request, next) => {
//   const update = {
//     headers: request.headers.append('Authorization', `Token ${localStorage.getItem('token')}`),
//   };
//   const requestNew = request.clone(update);
//   console.log("TEST");
//   return handler.handle(requestNew);
// };

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(
    private authService: AuthService,
  ) {
  }

  intercept(request: HttpRequest<any>, handler: HttpHandler): Observable<HttpEvent<any>> {
    const isRegistration = !!request.url.match(/\/auth\/users\/$/);
    const update: { headers?: HttpHeaders } = {};
    if (this.authService.token) {
      update['headers'] = request.headers.append('Authorization', `Token ${this.authService.token}`);
    }
    const requestNew = request.clone(update);
    return handler.handle(requestNew).pipe(
      catchError((error, caught): ObservableInput<any> => {
        if (error instanceof HttpErrorResponse) {
          console.log(error);
          const isError400 = error.status === 400;
          const isError401 = error.status === 401;
          const isAuthError = (isError400 || isError401) && !isRegistration;
          const isRegisterError = (isError400 || isError401) && isRegistration;
          const isOtherError = !isAuthError && !isRegisterError;
          if (isOtherError) {
            alert(`Ошибка сервера: ${error.status}`);
            throw error;
          }
          if (isAuthError) {
            alert('Ошибка авторизации');
            this.authService.logout();
          } else {
            throw error;
          }
        }
        return throwError(error);
      }));
  }
}
