# Nuclear
    Module which aids development tools for Nuke. Acting as a helper to common callable functions and class


#### Callback
```python
import nuclear
import nuke

with nuclear.CallBack():
    # Run sniped of code
    for node in nuke.allNodes():
        do_something_to_node(node)
    else:
        print("Operation complete")

# Exit and return the callback dictionary

```
#### Keep Selected
```python
import nuclear
import nuke

with nuclear.KeepSelected():
    # Run sniped of code
    for node in nuke.allNodes():
        do_something_to_node(node)
    else:
        print("Operation complete")
```

# Exit and return the callback dictionary
