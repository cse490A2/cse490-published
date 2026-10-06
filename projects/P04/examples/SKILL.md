---
name: meal-plan
description: Use when the user asks for a meal plan, what to cook this week, or dinner ideas.
---

# Weekly meal plan

Plan one week of dinners for one person who cooks at home.

## Before the work

1. Read `skills/meal-plan/memory.md`. It lists what the user can cook,
   what they liked, and what they want to avoid.
2. If `memory.md` is empty, ask two questions and wait for the answers:
   how many nights they cook this week, and one meal they made recently
   and liked.

## The plan

3. Pick one dinner per cooking night. Repeat nothing from the last two
   weeks in `memory.md`.
4. Keep every recipe inside what `memory.md` says the user can cook. A
   new technique appears at most once in the week, and the plan names it.
5. Show the plan as a table: night, dish, time to cook, the one thing to
   prep ahead.
6. Ask whether any night should change. Change only that night.

## The shopping list

7. Follow the shopping-list subskill in `skills/meal-plan/shopping-list/`.

## After the work

8. Write to `skills/meal-plan/memory.md`: the week's date, the final
   plan, and anything the user said they liked or want to avoid. Keep
   the earlier weeks. Say what you are about to write first.
