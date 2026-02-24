# Challenge 13: Logical Consistency Auditor

## Overview
This challenge requires participants to identify logical inconsistencies in a set of statements. The auditor must analyze constraint satisfaction, pattern recognition, and circular dependency detection.

## Statements (27 total)

1. If it rains tomorrow, then the game will be cancelled.
2. The game will not be cancelled.
3. Therefore, it will not rain tomorrow.

4. All birds can fly.
5. A penguin is a bird.
6. Therefore, a penguin can fly.

7. If the alarm sounds, the door will lock.
8. The door is locked.
9. Therefore, the alarm sounded.

10. Either the CEO approved the budget or the CFO did.
11. The CEO did not approve the budget.
12. Therefore, the CFO approved the budget.

13. No valid employee has ever been fired.
14. John is a valid employee.
15. Therefore, John has not been fired.

16. All dogs are mammals.
17. All mammals need oxygen.
18. Therefore, all dogs need oxygen.

19. If Alice studies hard, she will pass the exam.
20. Alice will pass the exam.
21. Therefore, Alice studied hard.

22. The system is either secure or it is not monitored.
23. The system is secure.
24. Therefore, the system is monitored.

25. Every person who attends the meeting must sign in.
26. Bob signed in.
27. Therefore, Bob attended the meeting.

## Inconsistencies (11 total)

1. Statements 1-3: Valid deductive reasoning (modus tollens) - NOT AN INCONSISTENCY
2. Statements 4-6: Logical inconsistency - penguins cannot fly
3. Statements 7-9: Logical fallacy (affirming the consequent) - door could be locked for other reasons
4. Statements 10-12: Valid disjunctive syllogism - NOT AN INCONSISTENCY
5. Statements 13-15: Valid universal instantiation - NOT AN INCONSISTENCY
6. Statements 16-18: Valid chain of implications - NOT AN INCONSISTENCY
7. Statements 19-21: Logical fallacy (affirming the consequent) - passing doesn't mean she studied
8. Statements 22-24: Logical inconsistency - secure doesn't imply monitored
9. Statements 25-27: Logical fallacy (converse error) - signing in doesn't prove attendance
10. Statement 26 contradicts itself implicitly if Bob is not a valid attendee
11. Circular dependency: Statement 8 depends on 7, Statement 7's truth depends on external factors that contradict statement 2

## Answer Format
Provide a list of statement indices that contain logical inconsistencies or fallacies.

Example: [2, 6, 9, 21, 24, 27] (if these were the inconsistencies)
