## Лабораторная работа 2 (обнуление)
### Задача
Реализовать LL-корректное удаление eplison-правил.

### Подсказки
1. Базовый алгоритм — в лекции 8. До его применения удалить все недостижимые и непорождающие нетерминалы и содержащие их правила. Учесть, что исходная грамматика допускает нетерминалы вида $[N_1 N_2]$, поэтому при присоединении контекста использовать разделитель (например, `+` или `->`), отсутствующий в исходном алфавите нетерминалов.
2. Если грамматика не LL(k), тогда алгоритм может зациклиться. Произойти это может, по лемме Розенкранца и Стирнса, только если в результате присоединения обнуляемого контекста возникнет нетерминал вида $[Φ_1 −> A(−> Φ_2 )?−> A(−> Φ_3 )?]$ (т.е. такой, в котором дважды присоединяется один и тот же обнуляемый нетерминал). $Φ_i$ — произвольные последовательности присоединённых нетерминалов. В таких случаях прерывать исполнение, печатать промежуточную грамматику, в которой появился проблемный нетерминал, и сообщать, что исходная грамматика — не LL(k).

### Синтаксис входных данных
```
rule ::= notterm '->' (term | notterm)* ('|' (term | notterm)+)*
term ::= [a-z]
notterm ::= '[' [A-Za-z]+ ']'
```