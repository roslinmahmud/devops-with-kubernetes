import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('todo');

  ngOnInit() {
    fetch('/api/image')
      .then(response => response.json())
      .then(data => {
        console.log('Image data:', data);
      })
      .catch(error => {
        console.error('Error fetching image:', error);
      });
  }
}
