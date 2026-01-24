import { Component, OnInit, signal, computed } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';

interface Todo {
  id: number;
  title: string;
  completed: boolean;
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('todo');
  imageURL = signal('');
  todos = signal<Todo[]>([]);
  newTodoTitle = signal('');

  activeTodos = computed(() => this.todos().filter(todo => !todo.completed));
  completedTodos = computed(() => this.todos().filter(todo => todo.completed));

  ngOnInit() {
    this.fetchImage();
    this.fetchTodos();
  }

  private fetchImage() {
    fetch('/api/image')
      .then(response => response.json())
      .then(data => {
        this.imageURL.set(data.image + '?ts=' + Date.now());
      })
      .catch(error => {
        console.error('Error fetching image:', error);
      });
  }

  private fetchTodos() {
    fetch('/api/todos')
      .then(response => response.json())
      .then(data => {
        this.todos.set(data);
      })
      .catch(error => {
        console.error('Error fetching todos:', error);
      });
  }

  createTodo() {
    if (!this.newTodoTitle().trim()) return;
    const newTodo = { id: 0, title: this.newTodoTitle(), completed: false };
    fetch('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newTodo)
    })
      .then(response => response.json())
      .then(todo => {
        this.todos.update(todos => [...todos, todo]);
        this.newTodoTitle.set('');
      })
      .catch(error => {
        console.error('Error creating todo:', error);
      });
  }

  markAsDone(todo: Todo) {
    fetch(`/api/todos/${todo.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...todo, completed: true })
    })
      .then(response => response.json())
      .then(updatedTodo => {
        this.todos.update(todos => 
          todos.map(t => t.id === updatedTodo.id ? updatedTodo : t)
        );
      })
      .catch(error => {
        console.error('Error updating todo:', error);
      });
  }
}
