import {Injectable} from '@angular/core';
import {HttpClient, HttpResponse} from '@angular/common/http';
import {lastValueFrom, map, Observable} from 'rxjs';
import {ApiService} from './api.service';
import {Router} from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
    private http: HttpClient,
    private router: Router,
    private apiService: ApiService,
  ) {
  }

  public set token(token: string) {
    localStorage.setItem('token', token);
  }

  public get token(): string {
    return localStorage.getItem('token') || '';
  }

  public async register(username: string, password: string): Promise<boolean> {
    const action = this.apiService.apiEndpoint + '/auth/users/';
    const data$ = this.http.post(action, {username, password});
    try {
      const data = await lastValueFrom(data$);
      // this.router.navigate(['/login']);
      alert(1);
      return true
    } catch (error) {
      const message1 = 'Ошибка регистрации:';
      const message2 = '';
      const message3 = JSON.stringify(error);
      // const message = [message1, message2, message3].join('\n\n');
      const message = [message1, message3].join('\n\n');
      console.log(error);
      console.error(error);
    }
    return false;
  }

  public async login(username: string, password: string): Promise<boolean> {
    const action = this.apiService.apiEndpoint + '/auth/token/login/';
    const data$ = this.http.post<{ auth_token: string }>(action, {username, password});
    try {
      const data = await lastValueFrom(data$);
      this.token = data.auth_token;
      this.router.navigate(['/']);
      return true;
    } catch (error) {
      console.error(error);
    }
    return false;
  }

  public logout() {
    this.token = '';
    this.router.navigate(['login']);
  }

}
