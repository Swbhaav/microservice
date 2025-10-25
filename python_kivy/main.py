# main.py (Enhanced Kivy Todo App)
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock

API_URL = "http://localhost:8000/todos/"

class TodoItem(BoxLayout):
    title = StringProperty("")
    done = BooleanProperty(False)
    todo_id = StringProperty("")

class TodoView(BoxLayout):
    todos = ListProperty([])
    loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Delay both binding and fetch until widget is fully initialized
        Clock.schedule_once(self._initialize, 0.5)
    
    def _initialize(self, dt):
        """Initialize after widget is ready"""
        # Bind to todos property to update UI when it changes
        self.bind(todos=self.update_todo_list)
        # Fetch todos
        self.fetch_todos()
    
    def update_todo_list(self, instance, value):
        """Update the UI when todos list changes"""
        # Check if widget is ready
        if 'todos_container' not in self.ids:
            return
            
        container = self.ids.todos_container
        container.clear_widgets()
        
        for todo in self.todos:
            item = TodoItem()
            item.title = todo.get("title", "")
            item.done = todo.get("done", False)
            item.todo_id = str(todo.get("id", ""))
            container.add_widget(item)

    def show_error(self, message):
        """Display error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def show_success(self, message):
        """Display success popup"""
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)

    def fetch_todos(self):
        """Fetch all todos from API"""
        self.loading = True
        try:
            resp = requests.get(API_URL, timeout=5)
            if resp.status_code == 200:
                self.todos = resp.json()
            else:
                self.show_error(f"Failed to fetch todos: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.show_error("Connection error. Check if backend is running.")
        except requests.exceptions.Timeout:
            self.show_error("Request timed out.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.loading = False

    def add_todo(self):
        """Add a new todo"""
        title = self.ids.input_title.text.strip()
        if not title:
            self.show_error("Please enter a title")
            return
        
        data = {"title": title, "description": ""}
        
        try:
            resp = requests.post(API_URL, json=data, timeout=5)
            if resp.status_code in [200, 201]:
                new = resp.json()
                # Create new list to trigger update
                self.todos = self.todos + [new]
                self.ids.input_title.text = ""
                self.show_success("Todo added!")
            else:
                self.show_error(f"Failed to add todo: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.show_error("Connection error. Check if backend is running.")
        except requests.exceptions.Timeout:
            self.show_error("Request timed out.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def toggle_done(self, todo_id, current_done):
        """Toggle todo completion status"""
        try:
            resp = requests.put(
                f"{API_URL}{todo_id}", 
                json={"done": not current_done},
                timeout=5
            )
            if resp.status_code == 200:
                updated = resp.json()
                # Create new list with updated todo
                new_todos = []
                for t in self.todos:
                    if str(t["id"]) == str(todo_id):
                        new_todos.append(updated)
                    else:
                        new_todos.append(t)
                self.todos = new_todos
            else:
                self.show_error(f"Failed to update todo: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.show_error("Connection error. Check if backend is running.")
        except requests.exceptions.Timeout:
            self.show_error("Request timed out.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def delete_todo(self, todo_id):
        """Delete a todo"""
        try:
            resp = requests.delete(f"{API_URL}{todo_id}", timeout=5)
            if resp.status_code == 200:
                # Create new list without deleted todo
                self.todos = [t for t in self.todos if str(t["id"]) != str(todo_id)]
                self.show_success("Todo deleted!")
            else:
                self.show_error(f"Failed to delete todo: {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.show_error("Connection error. Check if backend is running.")
        except requests.exceptions.Timeout:
            self.show_error("Request timed out.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def confirm_delete(self, todo_id, todo_title):
        """Show confirmation dialog before deleting"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"Delete '{todo_title}'?"))
        
        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        
        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def on_yes(instance):
            popup.dismiss()
            self.delete_todo(todo_id)
        
        def on_no(instance):
            popup.dismiss()
        
        btn_yes = Button(text='Yes')
        btn_yes.bind(on_press=on_yes)
        btn_no = Button(text='No')
        btn_no.bind(on_press=on_no)
        
        buttons.add_widget(btn_yes)
        buttons.add_widget(btn_no)
        content.add_widget(buttons)
        
        popup.open()

    def refresh_todos(self):
        """Refresh the todo list"""
        self.fetch_todos()

class TodoApp(App):
    def build(self):
        return TodoView()

if __name__ == "__main__":
    TodoApp().run()