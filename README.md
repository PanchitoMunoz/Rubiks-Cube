# Rubiks-Cube

Library that implements a representation of a
Rubik's Cube. The purpose of this implementation is
to use it for research purposes.

## How to use it?

The easiest way to create a Rubik's Cube is with
the `RubikCube` class. Here is an example:

```python
from rubiks_cube.cube import RubikCube
rc = RubikCube.from_dims((3, 2, 1))
print(rc)
```

Noting that a `RubikCube` instance is a hashable and immutable object (with the current methods).

![Representation of a Rubik's Cube of 3x2x1.](img/representation01.png)

### Making move on the Rubik's Cube

If you want to make a move on the Rubik's Cube,
you can do it like the example:

```python
from rubiks_cube.cube import RubikCube
from rubiks_cube.movements import CubeMove

rc = RubikCube.from_dims((3, 2, 1))
rc = rc.make_movements(CubeMove.L2)
print(rc)
```

![img.png](img/move_L2.png)

You can make a series of movements with a list of `CubeMove`:

```python
from rubiks_cube.cube import RubikCube
from rubiks_cube.movements import CubeMove

rc = RubikCube.from_dims((3, 2, 1))
rc = rc.make_movements([CubeMove.L2, CubeMove.U2])
print(rc)
```

![img.png](img/move_L2_U2.png)

Or with a string with the representation of `CubeMove`:

```python
from rubiks_cube.cube import RubikCube

rc = RubikCube.from_dims((3, 2, 1))
rc = rc.make_movements("L2 U2")
print(rc)
```

![img.png](img/move_L2_U2.png)

### Making the Graph

Given a set of permitted movements
<img src="https://latex.codecogs.com/svg.image?\bg{white}M" title="https://latex.codecogs.com/svg.image?\bg{white}M" />
(where the permitted movements are operations over the group of Rubik's Cube), for example,
<img src="https://latex.codecogs.com/svg.image?\bg{white}M&space;=&space;\{U^2,&space;R^2,&space;D^2\}" title="https://latex.codecogs.com/svg.image?\bg{white}M = \{U^2, R^2, D^2\}" />
.
We expect to create a graph
<img src="https://latex.codecogs.com/svg.image?\bg{white}G_M=(V,&space;E_M)" title="https://latex.codecogs.com/svg.image?\bg{white}G_M=(V, E_M)" />
where
<img src="https://latex.codecogs.com/svg.image?\bg{white}V&space;=&space;\{&space;r&space;|&space;r&space;\text{&space;is&space;a&space;Rubik's&space;Cube}&space;\}" title="https://latex.codecogs.com/svg.image?\bg{white}V = \{ r | r \text{ is a Rubik's Cube} \}" />
and
<img src="https://latex.codecogs.com/svg.image?\bg{white}E_M&space;=&space;\{&space;(r,&space;t)&space;\in&space;V&space;\times&space;V&space;|&space;t&space;=&space;m(r),\&space;m&space;\in&space;M&space;\}" title="https://latex.codecogs.com/svg.image?\bg{white}E_M = \{ (r, t) \in V \times V | t = m(r),\ m \in M \}" />
The described graph can be computed with the following instructions:

```python
from matplotlib import pyplot as plt

from rubiks_cube.graph import make_graph
from rubiks_cube.movements import CubeMove as CM
from rubiks_cube.plotters import GraphPlotter

g = make_graph(
    dims=(3, 2, 1),
    permitted_movements={CM.R2, CM.D2, CM.U2}
)
gp = GraphPlotter(g)
gp.compute_kamada_kawai_layout()
gp.find_bipartite()
gp.draw()
plt.show()
```

And it plots the following graph:
![A graph](img/graph.png)

