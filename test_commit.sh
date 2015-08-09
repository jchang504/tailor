#!/bin/bash

# TODO: add auto-generation of Usage section of README
nosetests && git commit -F delta
