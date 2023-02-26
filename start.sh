#!/bin/bash

cd API && python main.py &
cd "../Web App" && node index.js &
