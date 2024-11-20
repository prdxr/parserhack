import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {ApiService} from '../../services/api.service';
import {AuthService} from '../../services/auth.service';

@Component({
  selector: 'app-page-login',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './page-login.component.html',
  styleUrl: './page-login.component.scss'
})
export class PageLoginComponent {

  public username = '';
  public password = '';

  constructor(
    public apiService: ApiService,
    public authService: AuthService,
  ) {
  }

  // loginData = {
  //   username: '',
  //   password: ''
  // };


  // onLogin() {
  //   this.apiService.login(this.loginData).subscribe({
  //     next: (token) => {
  //       console.log(token);
  //       localStorage.setItem('token', token);
  //     },
  //     error: (error) => {
  //       console.error('login failed:', error);
  //     }
  //   });
  // }

  onLogin1() {
    this.authService.login(this.username, this.password);
  }
}
