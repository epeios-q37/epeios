#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2021 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os, sys, itertools


BLACK = -1
EMPTY = 0
WHITE = 1

TOKEN = {
  EMPTY: ' ',
  BLACK: 'X',
  WHITE: 'O'
}

def new_board():
  board = []

  for _ in range(8):
    board += [[EMPTY] * 8]

  board[3][3] = board[4][4] = BLACK
  board[4][3] = board[3][4] = WHITE

  return board

def has_my_piece(board, bw, x, y, delta_x, delta_y):
  "There is my piece in the direction of (delta_x, delta_y) from (x, y)."
  assert bw in (BLACK, WHITE)
  assert delta_x in (-1, 0, 1)
  assert delta_y in (-1, 0, 1)
  x += delta_x
  y += delta_y

  if x < 0 or x > 7 or y < 0 or y > 7 or board[x][y] == EMPTY:
    return False
  if board[x][y] == bw:
    return True
  return has_my_piece(board, bw, x, y, delta_x, delta_y)

def reversible_directions(board, bw, x, y):
  "Can put piece on (x, y) ? Return list of reversible direction tuple"
  assert bw in (BLACK, WHITE)

  directions = []
  if board[x][y] != EMPTY:
    return directions

  for d in itertools.product([-1, 1, 0], [-1, 1, 0]):
    if d == (0, 0):
      continue
    nx = x + d[0]
    ny = y + d[1]
    if nx < 0 or nx > 7 or ny < 0 or ny > 7 or board[nx][ny] != bw * -1:
      continue
    if has_my_piece(board, bw, nx, ny, d[0], d[1]):
      directions.append(d)
  return directions

def reverse_piece(board, bw, x, y, delta_x, delta_y):
  "Reverse pieces in the direction of (delta_x, delta_y) from (x, y) until bw."
  assert bw in (BLACK, WHITE)

  x += delta_x
  y += delta_y
  assert board[x][y] in (BLACK, WHITE)

  if board[x][y] == bw:
    return

  board[x][y] = bw
  reverse_piece(board, bw, x, y, delta_x, delta_y)  

def is_allowed(board, x, y, bw):
  if bw == EMPTY:
    return False
  else:
    return len(reversible_directions(board, bw, x, y)) != 0

def count(board, bwe):
  "Count pieces or empty spaces in the board"
  assert bwe in (BLACK, WHITE, EMPTY)
  n = 0
  for x in range(8):
    for y in range(8):
      if board[x][y] == bwe:
        n += 1
  return n    

def is_game_over(board):
  return count(board, EMPTY) == 0 or count(board, BLACK) == 0 or count(board, WHITE) == 0

def winner(board):
  b = count(board, BLACK)
  w = count(board, WHITE)

  return (w>b) - (b>w)

class Reversi:
  def __init__(self):
    self.bw = None

  def init(self, bw):
    self.bw = bw  