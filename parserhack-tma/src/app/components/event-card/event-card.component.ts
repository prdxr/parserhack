import {Component, Input} from '@angular/core';
import { animate, state, style, transition, trigger } from '@angular/animations';
import {NgForOf} from '@angular/common';
import {IEventTag} from '../../services/api.service';

@Component({
  selector: 'app-event-card',
  standalone: true,
  imports: [
    NgForOf
  ],
  templateUrl: './event-card.component.html',
  styleUrl: './event-card.component.scss',
  animations : [
    trigger('panelState', [
      state('closed', style({ height: '32px', overflow: 'hidden' })),
      state('open', style({ height: '*' })),
      transition('closed <=> open', animate('300ms ease-in-out')),
    ]),
  ],
})
export class EventCardComponent {
  folded = 'closed';
  @Input() eventTitle: string = '';
  @Input() eventType: string = '';
  @Input() eventTags: IEventTag[] = [];

  toggleFold(){
    this.folded = this.folded === 'open' ? 'closed' : 'open';
    console.log(this.eventTags)
  }
}
