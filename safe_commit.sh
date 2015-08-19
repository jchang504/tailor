#!/bin/bash

# Run from the Git parent directory!
# TODO: add auto-generation of Usage section of README
! grep -rin --exclude=safe_commit.sh '#\s*BLOCKING TODO' . &&
! grep -rn '.\{80\}' *.{py,md} &&
nosetests &&
git commit -F delta
