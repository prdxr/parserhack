import { Component } from '@angular/core';
import {AuthService} from '../../services/auth.service';
import {Router} from '@angular/router';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-page-settings',
  standalone: true,
  imports: [
    NgIf
  ],
  templateUrl: './page-settings.component.html',
  styleUrl: './page-settings.component.scss'
})
export class PageSettingsComponent {

  constructor(
    public router: Router,
    public authService: AuthService,
  ) {
  }

  protected readonly AuthService = AuthService;

  register() {
    this.router.navigate(['register']);
  }
}
