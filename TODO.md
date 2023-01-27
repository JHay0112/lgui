1. Highlight selected component ?

2. del -> Delete selected component

3. Add stretchy wires to components rather than resizing

4. Add coloured components

5. Click on component to edit attributes: name, kind, value.  For
example, DC, AC, transient kinds of source.

6. Add ports, open circuits (how to show?)

7. Add formatting options: standard, canonical, ZPK, time-constant, etc.

8. Add transform options: time, Laplace, Fourier, etc.

9. Add misc operations: poles, zeros, etc.

10. Add plots: time, frequency, pole-zero, etc.  Need dialogs to
specify time/frequency range

11. Add box where can enter Lcapy commands to manipulate current
expression and box to display result.  The entry box could be like a
shell (using eval) and could use cct to denote current circuit, result
to denote current result etc.

12. Render output expression with LaTeX

13. Show current through component.  For wires this is tricky and will
require some Lcapy magic.  Need to sum all the currents coming into
the branch node.  This requires recursion if connected to other wires.
Stop if reach one of the branch nodes

14. Undo....

15. Redo...

16. Move components

17. Rotate components?  Perhaps just delete and re-enter but lose
attributes unless clever

18. Lots more components to add.  Perhaps automagically go through
    lcapy.schemcpts to add them.

19. Entry of exotic components, say xtal.  Need a special prefix, say x.
xxtal for a crystal, xcpe for a CPE, etc.
