import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {DatePipe} from '@angular/common';

export interface IEventTag {
  tag_code: number;
  description: string;
}

export interface IEventType {
  type_code: number;
  description: string;
}

export interface IApiRow {
  id: number;
  tags: IEventTag[];
  type_of_event: IEventType;
  title: string;
  description: string;
  addresses: string;
  start_date: string;
  registration_deadline: string;
  end_date: string;
  url: string;
  is_free: boolean;
}

export type TApiData = IApiRow[];

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  // public apiEndpoint = "http://88.218.67.139:83";
  public apiEndpoint = "https://ph-api-gw.temp.kitt-club.ru/api"
  public isLoading = false;

  constructor(
    private http: HttpClient
  ) {
  }

  public authToken: string = '';

  public initialize(): any {
    const authEndpoint = this.apiEndpoint + '/auth/token/login/';
    return this.http.post(this.apiEndpoint, JSON.stringify(
      {
        "username": "root",
        "password": "root"
      }
    ));
  }

  public getData(): Observable<TApiData> {
    const action = this.apiEndpoint + '/hackaton/';
    const headers = {
      // "Authorization": "Token ea2cf2f4d0406654a06d23eb9a8524e2d414e3fe"
    };
    this.isLoading = true;
    const result = this.http.get<any[]>(action, {headers});
    result.subscribe(() => this.isLoading = false);
    return result;
  }

}
