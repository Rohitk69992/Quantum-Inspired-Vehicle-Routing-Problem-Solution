#!/usr/bin/env python3
"""
scripts/make_figures.py
Generates publication-quality PDF vector figures and high-resolution PNGs
from experimental results.
"""

import os
import sys
from scripts.generate_figures import generate_publication_figures

def generate_all_figures():
    generate_publication_figures()

if __name__ == "__main__":
    generate_all_figures()
