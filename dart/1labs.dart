import 'dart:io';

void task1Variables() {
  
  String name = 'Алексей';
  int age = 20;
  double averageGrade = 4.75;
  bool isStudent = true;

  print('Имя: $name [${name.runtimeType}]');
  print('Возраст: $age [${age.runtimeType}]');
  print('Средний балл: $averageGrade [${averageGrade.runtimeType}]');
  print('Студент: ${isStudent ? "да" : "нет"} [${isStudent.runtimeType}]');
  print('');
}

void task2FizzBuzz() {

  List<String> results = [];
  for (int i = 1; i <= 100; i++) {
    if (i % 3 == 0 && i % 5 == 0) {
      results.add('FizzBuzz');
    } else if (i % 3 == 0) {
      results.add('Fizz');
    } else if (i % 5 == 0) {
      results.add('Buzz');
    } else {
      results.add(i.toString());
    }
  }
  print(results.join(', '));
  print('');
}

void task3CountVowels([String input = 'Flutter']) {
  const String vowels = 'aeiouyаеёиоуыэюяі';
  int count = 0;

  for (int i = 0; i < input.length; i++) {
    String char = input[i].toLowerCase();
    if (vowels.contains(char)) {
      count++;
    }
  }

  print('Слово: $input');
  print('Гласных букв: $count');
  print('');
}

class SmartCalculator {
  
  static double calculate(String? rawA, String? rawB, String? rawOp) {
    
    final String strA = rawA?.trim() ?? '';
    final String strB = rawB?.trim() ?? '';
    final String op = rawOp?.trim() ?? '+';

    final double? a = double.tryParse(strA);
    final double? b = double.tryParse(strB);
    if (a == null || b == null) {
      throw FormatException(
        'Некорректный ввод числа: "${a == null ? strA : strB}"',
      );
    }

    final bool isZeroDivision = (op == '/' || op == '%') && b == 0;
    if (isZeroDivision) {
      throw UnsupportedError(
        op == '/' ? 'Ошибка: деление на ноль!' : 'Ошибка: остаток от деления на ноль!',
      );
    }

    switch (op) {
      case '+':
        return a + b;
      case '-':
        return a - b;
      case '*':
        return a * b;
      case '/':
        return a / b;
      case '%':
        return a % b;
      default:
        throw ArgumentError('Неизвестный оператор: "$op"');
    }
  }

  static double evaluateExpression(String expression) {
    final tokens = expression.trim().split(RegExp(r'\s+'));
    if (tokens.isEmpty || tokens.length % 2 == 0) {
      throw FormatException('Некорректный формат выражения: "$expression"');
    }

    List<double> values = [];
    List<String> ops = [];

    for (int i = 0; i < tokens.length; i++) {
      if (i.isEven) {
        final val = double.tryParse(tokens[i]);
        if (val == null) {
          throw FormatException('Некорректное число: "${tokens[i]}"');
        }
        values.add(val);
      } else {
        ops.add(tokens[i]);
      }
    }

    int i = 0;
    while (i < ops.length) {
      if (ops[i] == '*' || ops[i] == '/' || ops[i] == '%') {
        double res = calculate(
          values[i].toString(),
          values[i + 1].toString(),
          ops[i],
        );
        values[i] = res;
        values.removeAt(i + 1);
        ops.removeAt(i);
      } else {
        i++;
      }
    }

    double result = values[0];
    for (int j = 0; j < ops.length; j++) {
      result = calculate(
        result.toString(),
        values[j + 1].toString(),
        ops[j],
      );
    }
    return result;
  }
}

void task4SmartCalculator() {
  print('=== ЗАДАНИЕ 4: Умный калькулятор с обработкой ошибок ===');

  final testCases = [
    ['15', '4', '+'],
    ['15', '4', '-'],
    ['15', '4', '*'],
    ['15', '4', '/'],
    ['15', '4', '%'],
    ['10', '0', '/'], 
    ['abc', '5', '+'], 
    ['10', '5', '^'], 
  ];

  for (var tc in testCases) {
    try {
      double res = SmartCalculator.calculate(tc[0], tc[1], tc[2]);
      
      String formatted = (res == res.roundToDouble())
          ? res.toInt().toString()
          : res.toStringAsFixed(2);
      print('${tc[0]}${tc[2]} ${tc[1]} =$formatted');
    } catch (e) {
      print('Выражение "${tc[0]}${tc[2]} ${tc[1]}" -> $e');
    }
  }

  String expr = '10 + 2 * 6 - 15 / 3 + 7 % 4';
  print('Выражение с приоритетом: $expr =${SmartCalculator.evaluateExpression(expr)}');
  print('');
}

class MatrixCalculator {
  static void validateMatrix(List<List<double>> m) {
    if (m.isEmpty || m[0].isEmpty) {
      throw ArgumentError('Матрица не может быть пустой.');
    }
    int cols = m[0].length;
    for (var row in m) {
      if (row.length != cols) {
        throw ArgumentError('Строки матрицы имеют разную длину.');
      }
    }
  }

  static List<List<double>> add(List<List<double>> a, List<List<double>> b) {
    validateMatrix(a);
    validateMatrix(b);
    if (a.length != b.length || a[0].length != b[0].length) {
      throw ArgumentError(
        'Несовместимые размеры матриц для сложения: '
        '${a.length}x${a[0].length} и ${b.length}x${b[0].length}',
      );
    }
    return List.generate(
      a.length,
      (i) => List.generate(a[0].length, (j) => a[i][j] + b[i][j]),
    );
  }

  static List<List<double>> subtract(List<List<double>> a, List<List<double>> b) {
    validateMatrix(a);
    validateMatrix(b);
    if (a.length != b.length || a[0].length != b[0].length) {
      throw ArgumentError(
        'Несовместимые размеры матриц для вычитания: '
        '${a.length}x${a[0].length} и ${b.length}x${b[0].length}',
      );
    }
    return List.generate(
      a.length,
      (i) => List.generate(a[0].length, (j) => a[i][j] - b[i][j]),
    );
  }

  static List<List<double>> multiplyByScalar(List<List<double>> a, double scalar) {
    validateMatrix(a);
    return List.generate(
      a.length,
      (i) => List.generate(a[0].length, (j) => a[i][j] * scalar),
    );
  }

  static List<List<double>> multiply(List<List<double>> a, List<List<double>> b) {
    validateMatrix(a);
    validateMatrix(b);
    if (a[0].length != b.length) {
      throw ArgumentError(
        'Несовместимые размеры для умножения матриц: '
        'столбцов A (${a[0].length}) != строк B (${b.length})',
      );
    }
    int rowsA = a.length;
    int colsA = a[0].length;
    int colsB = b[0].length;

    return List.generate(rowsA, (i) {
      return List.generate(colsB, (j) {
        double sum = 0;
        for (int k = 0; k < colsA; k++) {
          sum += a[i][k] * b[k][j];
        }
        return sum;
      });
    });
  }

  static List<List<double>> transpose(List<List<double>> a) {
    validateMatrix(a);
    return List.generate(
      a[0].length,
      (j) => List.generate(a.length, (i) => a[i][j]),
    );
  }

  static double determinant(List<List<double>> a) {
    validateMatrix(a);
    int n = a.length;
    if (n != a[0].length) {
      throw ArgumentError(
        'Определитель можно вычислить только для квадратной матрицы (получена ${n}x${a[0].length}).',
      );
    }
    if (n == 1) return a[0][0];
    if (n == 2) return a[0][0] * a[1][1] - a[0][1] * a[1][0];

    double det = 0;
    for (int col = 0; col < n; col++) {
      List<List<double>> subMatrix = [];
      for (int i = 1; i < n; i++) {
        List<double> row = [];
        for (int j = 0; j < n; j++) {
          if (j != col) row.add(a[i][j]);
        }
        subMatrix.add(row);
      }
      double sign = (col % 2 == 0) ? 1.0 : -1.0;
      det += sign * a[0][col] * determinant(subMatrix);
    }
    return det;
  }

  static void printMatrix(String title, List<List<double>> m) {
    print(title);
    for (var row in m) {
      print('  [ ${row.map((e) => e.toStringAsFixed(1).padLeft(5)).join(', ')} ]');
    }
  }
}

void task5MatrixCalculator() {
  List<List<double>> matrixA = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 10]
  ];
  List<List<double>> matrixB = [
    [9, 8, 7],
    [6, 5, 4],
    [3, 2, 1]
  ];

  MatrixCalculator.printMatrix('Матрица A:', matrixA);
  MatrixCalculator.printMatrix('Матрица B:', matrixB);
  MatrixCalculator.printMatrix('Сложение (A + B):', MatrixCalculator.add(matrixA, matrixB));
  MatrixCalculator.printMatrix('Вычитание (A - B):', MatrixCalculator.subtract(matrixA, matrixB));
  MatrixCalculator.printMatrix('Умножение A на число 2.5:', MatrixCalculator.multiplyByScalar(matrixA, 2.5));
  MatrixCalculator.printMatrix('Умножение матриц (A * B):', MatrixCalculator.multiply(matrixA, matrixB));
  MatrixCalculator.printMatrix('Транспонирование A^T:', MatrixCalculator.transpose(matrixA));
  print('Определитель det(A): ${MatrixCalculator.determinant(matrixA)}');

  try {
    MatrixCalculator.add(matrixA, [
      [1, 2],
      [3, 4]
    ]);
  } catch (e) {
    print('Проверка обработки ошибки размерности -> $e');
  }
}

void main() {
  task1Variables();
  task2FizzBuzz();
  task3CountVowels('Flutter');
  task4SmartCalculator();
  task5MatrixCalculator();
}