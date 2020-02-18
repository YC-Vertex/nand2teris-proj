// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(KBD_LISTENER)
@color
M = 0
@KBD
D = M
@SET_COLOR
D; JEQ
@color
M = -1 

(SET_COLOR)
// color_prv == color
@color_prv
D = M
@color_prv_cp
M = D
@color
D = M
@color_prv
M = D
// if color == color_prv, unchanged
@color_prv_cp
D = D - M
@KBD_LISTENER
D; JEQ
// else, set color
@KBD
D = A
@ptr
M = D

(LOOP)
// jump out logic
@ptr
D = M
@SCREEN
D = D - A
@KBD_LISTENER
D; JEQ
// loop body
@ptr
M = M - 1
@color
D = M
@ptr
A = M
M = D
@LOOP
0; JMP
