import 'dart:math';

class MathProcessor {
  final List<double> numbers;
  MathProcessor(this.numbers);
  List<double> process(double Function(double) handler) => numbers.map(handler).toList();
  static List<double> getRandomNumbers(int count) =>
      List.generate(count, (_) => Random().nextDouble() * 10);
}

abstract class Shape {
  Shape(); 
  double area();
  factory Shape.fromJson(Map<String, dynamic> json) {
    if (json['type'] == 'circle') return Circle(json['radius'].toDouble());
    if (json['type'] == 'rectangle') return Rectangle(json['width'].toDouble(), json['height'].toDouble());
    throw ArgumentError('Unknown shape');
  }
}

class Circle extends Shape {
  final double radius;
  Circle(this.radius);
  @override
  double area() => pi * radius * radius;
  @override
  String toString() => 'Circle(area: ${area().toStringAsFixed(2)})';
}

class Rectangle extends Shape {
  final double width, height;
  Rectangle(this.width, this.height);
  @override
  double area() => width * height;
  @override
  String toString() => 'Rectangle(area: ${area().toStringAsFixed(2)})';
}

class PasswordValidator {
  static const int minLength = 8;
  static bool validate(String password) =>
      password.length >= minLength && RegExp(r'[0-9]').hasMatch(password);
}
class BankAccount {
  final String accountNumber;
  double _balance = 0;
  final String ownerName;

  BankAccount(this.accountNumber, this.ownerName);
  void deposit(double amount) {
    if (amount > 0) _balance += amount;
  }
  bool withdraw(double amount) {
    if (amount > _balance || amount <= 0) return false;
    _balance -= amount;
    return true;
  }
  void displayBalance() => print('Счёт $accountNumber ($ownerName): $_balance');
}

abstract class Character {
  final String name;
  double health = 100;
  Character(this.name);
  void attack();
  void defend(double damage) {
    health -= damage;
    print('$name получает $damage урона. Осталось HP: $health');
  }
}

class Warrior extends Character {
  Warrior(super.name);
  @override
  void attack() => print('$name (Воин) наносит мощный удар!');
}

void main() {
  
  final mp = MathProcessor([2.0, 3.0]);
  print('Квадраты: ${mp.process((x) => x * x)}');

  final shape1 = Shape.fromJson({'type': 'circle', 'radius': 5});
  final shape2 = Shape.fromJson({'type': 'rectangle', 'width': 4, 'height': 6});
  print(shape1);
  print(shape2);

  print('Пароль "Dart2026": ${PasswordValidator.validate("Dart2026")}');

  final acc = BankAccount('1234567890', 'Иван');
  acc.deposit(1500);
  acc.withdraw(500);
  acc.displayBalance();

  final w = Warrior('Артас');
  w.attack();
  w.defend(20);
}
