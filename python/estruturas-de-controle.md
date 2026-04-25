# 4. Estruturas de Decisão (`if`, `elif`, `else`)

O `if` permite que o programa tome decisões baseadas em condições. Aqui, a **indentação** (o espaço no início da linha) é obrigatória e fundamental.

### Operadores de Comparação:

- `==` Igual a
- `!=` Diferente de
- `>` Maior que
- `<` Menor que
- `>=` Maior ou igual
- `<=` Menor ou igual

### Exemplo Prático: Sistema de Notas

Imagine que precisamos saber se um aluno foi aprovado:

```python
nota = float(input("Digite a nota final: "))

if nota >= 60:
    print("Parabéns! Você foi aprovado.")
elif nota >= 40:
    print("Você está de recuperação.")
else:
    print("Infelizmente você foi reprovado.")
```

## Exercício de Fixação

Tente escrever um código que leia um número e diga se ele é **Par** ou **Ímpar**.
_Dica: use o operador de resto da divisão `% 2`._
