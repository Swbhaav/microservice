import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const String API_URL = "http://10.0.2.2:8000/todos/";

class Todo {
  int id;
  String title;
  String? description;
  bool done;

  Todo({
    required this.id,
    required this.title,
    this.description,
    required this.done,
  });

  factory Todo.fromJson(Map<String, dynamic> json) {
    return Todo(
      id: json["id"],
      title: json["title"],
      description: json["description"],
      done: json["done"],
    );
  }

  Map<String, dynamic> toJson() {
    return {"title": title, "description": description, "done": done};
  }
}

void main() {
  runApp(TodoApp());
}

class TodoApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(title: 'Flutter Todo', home: TodoPage());
  }
}

class TodoPage extends StatefulWidget {
  @override
  State<TodoPage> createState() => _TodoPageState();
}

class _TodoPageState extends State<TodoPage> {
  List<Todo> _todos = [];
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    fetchTodos();
  }

  Future<void> fetchTodos() async {
    final resp = await http.get(Uri.parse(API_URL));
    if (resp.statusCode == 200) {
      final List<dynamic> list = json.decode(resp.body);
      setState(() {
        _todos = list.map((e) => Todo.fromJson(e)).toList();
      });
    } else {
      // handle error
      print("Failed to fetch todos: ${resp.statusCode}");
    }
  }

  Future<void> addTodo(String title) async {
    final resp = await http.post(
      Uri.parse(API_URL),
      headers: {"Content-Type": "application/json"},
      body: json.encode({"title": title, "description": ""}),
    );
    if (resp.statusCode == 200 || resp.statusCode == 201) {
      final newTodo = Todo.fromJson(json.decode(resp.body));
      setState(() {
        _todos.add(newTodo);
      });
      _controller.clear();
    } else {
      print("Failed to create todo: ${resp.statusCode}");
    }
  }

  Future<void> toggleDone(Todo todo) async {
    final resp = await http.put(
      Uri.parse(API_URL + todo.id.toString()),
      headers: {"Content-Type": "application/json"},
      body: json.encode({"done": !todo.done}),
    );
    if (resp.statusCode == 200) {
      final updated = Todo.fromJson(json.decode(resp.body));
      setState(() {
        int idx = _todos.indexWhere((t) => t.id == updated.id);
        if (idx >= 0) {
          _todos[idx] = updated;
        }
      });
    } else {
      print("Failed to update todo: ${resp.statusCode}");
    }
  }

  Future<void> deleteTodo(int id) async {
    final resp = await http.delete(Uri.parse(API_URL + id.toString()));
    if (resp.statusCode == 200) {
      setState(() {
        _todos.removeWhere((t) => t.id == id);
      });
    } else {
      print("Failed to delete: ${resp.statusCode}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Flutter Todo Microservice')),
      body: Column(
        children: [
          Padding(
            padding: EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(hintText: 'Enter todo title'),
                  ),
                ),
                ElevatedButton(
                  onPressed: () {
                    String t = _controller.text.trim();
                    if (t.isNotEmpty) {
                      addTodo(t);
                    }
                  },
                  child: Text('Add'),
                ),
              ],
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: fetchTodos,
              child: ListView.builder(
                itemCount: _todos.length,
                itemBuilder: (context, index) {
                  final todo = _todos[index];
                  return ListTile(
                    title: Text(
                      todo.title,
                      style: TextStyle(
                        decoration: todo.done
                            ? TextDecoration.lineThrough
                            : null,
                      ),
                    ),
                    leading: Checkbox(
                      value: todo.done,
                      onChanged: (val) {
                        toggleDone(todo);
                      },
                    ),
                    trailing: IconButton(
                      icon: Icon(Icons.delete),
                      onPressed: () {
                        deleteTodo(todo.id);
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
