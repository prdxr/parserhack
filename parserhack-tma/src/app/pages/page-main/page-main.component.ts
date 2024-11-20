import { Component } from '@angular/core';
import {NgForOf, NgIf} from '@angular/common';
import {ApiService, TApiData} from '../../services/api.service';
import {Router} from '@angular/router';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {EventCardComponent} from '../../components/event-card/event-card.component';
import {PrettyDatePipe} from '../../pipes/pretty-date.pipe';

@Component({
  selector: 'app-page-main',
  standalone: true,
  imports: [
    NgForOf,
    EventCardComponent,
    PrettyDatePipe,
    NgIf
  ],
  templateUrl: './page-main.component.html',
  styleUrl: './page-main.component.scss',
})
export class PageMainComponent {

  public user = 'tim'; // PLACEHOLDER
  public data: TApiData = [];

  constructor(
    public apiService: ApiService
  ) {
    // this.apiService.initialize();
    setTimeout(() => {
      this.getData();
    }, 1000);
  }

  public getData() {
    // console.log("INITIALIZING API Endpoint, TOKEN: ", this.apiService.authToken);
    this.apiService.getData().subscribe(data => {
      this.data = data;
    })
  }
}
