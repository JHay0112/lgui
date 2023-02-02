1. Highlight selected component ?

3. Add stretchy wires to components rather than resizing

4. Add coloured components

5. Click on component to edit attributes: name, kind, value.  For
example, DC, AC, transient kinds of source.

6. Add ports, open circuits (how to show?)

9. Add misc operations: poles, zeros, etc.

13. Show current through component.  For wires this is tricky and will
require some Lcapy magic.  Need to sum all the currents coming into
the branch node.  This requires recursion if connected to other wires.
Stop if reach one of the branch nodes

15. Redo...

16. Move components

17. Rotate components?  Perhaps just delete and re-enter but lose
attributes unless clever

18. Lots more components to add.  Perhaps automagically go through
    lcapy.schemcpts to add them.

19. Entry of exotic components, say xtal.  Need a special prefix, say x.
xxtal for a crystal, xcpe for a CPE, etc.

20. Configuration file

21. User levels to hide many options

22. Make resistors a little shorter

23. Add numerical analysis

24. Draw components in selected colours, etc.
