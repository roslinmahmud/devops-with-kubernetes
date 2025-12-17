import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('todo');
  imageURL = signal('');

  ngOnInit() {
    fetch('/api/image')
      .then(response => response.json())
      .then(data => {
        console.log('Image data:', data);
        this.imageURL.set(data.image + '?ts=' + Date.now());
      })
      .catch(error => {
        console.error('Error fetching image:', error);
      });
  }
}
