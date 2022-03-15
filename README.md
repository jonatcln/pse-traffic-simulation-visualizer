# PSE Traffic Simulation Visualizer

Script to easily visualize traffic simulations (made for the PSE course)
via plain text data output.

![Visualizer Preview](assets/preview.gif)

## Requirements

This script requires Python 3 and Pygame.

Tested with:

- Python 3.8.10
- Pygame 2.1.2
- Ubuntu 20.04

You can install Pygame using `pip3 install pygame` or similar.

## Usage

The script reads its data from stdin before launching the visualization. The
text [data format](#data-format) is described below.

You can use the following
command to pipe the output of your simulation to the visualizer (assuming
`./trafficsimulation` runs the simulation and writes its output to stdout):

```sh
./trafficsimulation | python3 visualize.py
```

You can configure the initial window dimensions, playback rate, colors, etc. at
the top of the script.

## Data format

The visualizer reads the data from stdin line by line, where each line should
contain the next simulation 'frame'. Here is an example of what such a frame
should look like:

```plain
{
  "time": 0.0166,
  "roads": [
    {
      "name": "Arcade Street",
      "length": 500,
      "cars": [ {"x": 20}, {"x": 0} ],
      "lights": [ {"x": 300, "green": 0} ]
    },
    {
      "name": "Gold Avenue",
      "length": 400,
      "cars": [ {"x": 0} ],
      "lights": [ {"x": 200, "green": 0} ]
    }
  ]
}
```

_Note that each frame should be on its own single line._
_The example is split over multiple lines for readability only._

The `"time"` is the current frame's 'timestamp'. For now, it is only shown but
has no further semantic value. The `"x"` in cars and traffic lights are their
positions. And `"green"` tells the current color of a certain traffic light:
`1` means green, `0` means red.

## License

Licensed under the [AGPL-3.0 License](LICENSE).
