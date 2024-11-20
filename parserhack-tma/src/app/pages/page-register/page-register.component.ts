import { Component } from '@angular/core';
import {ApiService} from '../../services/api.service';
import {FormsModule} from '@angular/forms';
import {AuthService} from '../../services/auth.service';

@Component({
  selector: 'app-page-register',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './page-register.component.html',
  styleUrl: './page-register.component.scss'
})
export class PageRegisterComponent {

  public username = '';
  public password = '';


  constructor(
    public apiService: ApiService,
    public authService: AuthService,
  ) {
  }

  onRegister() {
    this.authService.register(this.username, this.password);
  }

}
