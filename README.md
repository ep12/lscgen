# lscgen
***WIP***

***lscgen****.py* generates a dircolors-like output from a human-readable config file.

## Installation
- `git clone` to your preferred location, for example **~/**.
- use lscgen.py everytime:
	```sh
	if [ -x ~/lscgen/lscgen.py ]; then
		eval "$(~/lscgen/lscgen.py -q ~/lscgen/theme.cfg)"
	fi
	```