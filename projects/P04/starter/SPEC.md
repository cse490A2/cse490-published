# explain.py

A program that explains a piece of Python from its structure. No model is
involved: it parses the code with Python's ast module, recognizes constructs,
and assembles sentences. The same input always gives the same output.

## Commands

    python explain.py <file.py>           the explanation
    python explain.py --facts <file.py>   the facts it found, one per line
    python explain.py score               facts covered over snippets/

score reads every snippets/NN.py, runs the same fact finder on it, compares
with snippets/NN.facts, and prints three things: facts covered, facts total,
and PASS or below target. Exit 0 on PASS, 1 otherwise.

Target: 71 of the 79 public facts.

## Facts

One per line, in this vocabulary and no other. Order does not matter. A
fact that is true of the file appears once, however many times the code
does it.

    function <name>            defines a function
    class <name>               defines a class
    import <module>            imports a module (the name after import or
                               from)
    for                        uses a for loop
    while                      uses a while loop
    comprehension              builds a list, dict or set in one expression
    recursive <name>           a function that calls itself
    catches <Error>            a try that catches that error
    raises <Error>             raises that error
    returns                    a function returns a value
    file-io                    opens, reads or writes a file
    calls <module>.<name>      calls a function from an imported module

## Rules

- Standard library only. No network.
- Deterministic: the same file gives the same output every time.
- The explanation's style, order, depth and voice are decided with the
  person who will read it. The score never reads the explanation; it reads
  --facts.

## snippets/

snippets/01.py through snippets/20.py, each with its NN.facts beside it.
More of the same shape are held back and run after submission.
