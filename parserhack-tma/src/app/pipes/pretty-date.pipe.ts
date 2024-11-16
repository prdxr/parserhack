import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
  name: 'prettyDate',
  standalone: true
})
export class PrettyDatePipe implements PipeTransform {

  transform(value: string, emptyString = "-"): string {
    const dt = new Date(value);
    if (dt.getTime() === 0) {
      return emptyString;
    }
    const day = dt.getDate().toLocaleString('ru-RU', {minimumIntegerDigits: 2});
    const month = (dt.getMonth() + 1).toLocaleString('ru-RU', {minimumIntegerDigits: 2});
    const year = dt.getFullYear();
    const hours = dt.getHours().toLocaleString('ru-RU', {minimumIntegerDigits: 2});
    const minutes = dt.getMinutes().toLocaleString('ru-RU', {minimumIntegerDigits: 2});;
    return `${day}.${month}.${year} ${hours}:${minutes}`;
    // return dt.getDate() + '.' + (dt.getMonth() + 1) + '.' + dt.getFullYear() + " " + dt.getHours() + ":" + dt.getMinutes();
  }

}
