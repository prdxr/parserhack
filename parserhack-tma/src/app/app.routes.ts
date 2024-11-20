import { Routes } from '@angular/router';
import {PageMainComponent} from './pages/page-main/page-main.component';
import {PageEventsComponent} from './pages/page-events/page-events.component';
import {PageSettingsComponent} from './pages/page-settings/page-settings.component';
import {PageRegisterComponent} from './pages/page-register/page-register.component';
import {PageLoginComponent} from './pages/page-login/page-login.component';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'main'
  },
  {
    path: 'main',
    component: PageMainComponent
  },
  {
    path: 'events',
    component: PageEventsComponent
  },
  {
    path: 'settings',
    component: PageSettingsComponent
  },
  {
    path: 'register',
    component: PageRegisterComponent
  },
  {
    path: 'login',
    component: PageLoginComponent
  }
];
