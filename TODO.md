1. Highlight selected component ?

2. Add stretchy wires to components rather than resizing

3. Add coloured components

4. Click on component to edit attributes: name, kind, value.  For
example, DC, AC, transient kinds of source.

5. Add ports, open circuits (how to show?)

6. Add misc operations: poles, zeros, etc.

7. Show current through component.  For wires this is tricky and will
require some Lcapy magic.  Need to sum all the currents coming into
the branch node.  This requires recursion if connected to other wires.
Stop if reach one of the branch nodes

8. Redo...

9. Move components

10. Rotate components?  Perhaps just delete and re-enter but lose
attributes unless clever

11. Lots more components to add.  Perhaps automagically go through
    lcapy.schemcpts to add them.

12. Entry of exotic components, say xtal.  Need a special prefix, say x.
xxtal for a crystal, xcpe for a CPE, etc.

13. Configuration file

14. User levels to hide many options

15. Make resistors a little shorter

16. Add numerical analysis

17. Draw components in selected colours, etc.

18. Draw port nodes

19. Zoom/pan schematic
