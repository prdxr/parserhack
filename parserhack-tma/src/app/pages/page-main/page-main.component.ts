import { Component } from '@angular/core';
import {NgForOf} from '@angular/common';
import {ApiService, TApiData} from '../../services/api.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-page-main',
  standalone: true,
  imports: [
    NgForOf
  ],
  templateUrl: './page-main.component.html',
  styleUrl: './page-main.component.scss'
})
export class PageMainComponent {

  public user = 'tim'; // PLACEHOLDER
  public data: TApiData = [];

  constructor(
    public apiService: ApiService
  ) {
    setTimeout(() => {
      this.getData();
    }, 1000);
  }

  public getData() {
    this.apiService.authToken = this.apiService.initialize();
    console.log("INITIALIZING API Endpoint, TOKEN: ", this.apiService.authToken);
    this.apiService.getData().subscribe(data => {
      this.data = data;
    })
  }

}
