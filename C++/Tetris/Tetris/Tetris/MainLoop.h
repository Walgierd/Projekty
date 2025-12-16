#include "IntroTetris.h"
#include <iostream>
#include <conio.h>
#include <ctime>
#include <chrono>
#include <windows.h>
#include <thread>
#include "Block.h"
#include "Board.h"

void mainLoop();
static void processInput(Board& board, Block& block, bool& playerMove, bool& gamePaused);
void hideCursor();
void pauseGame(Board& board, bool& gamePaused);

void mainLoop() {
    auto lastTime = std::chrono::high_resolution_clock::now();
    const int boardWidth = 10;
    const int boardHeight = 20;
    Board board(boardWidth, boardHeight);
    Block::Type randomBlockType = static_cast<Block::Type>(rand() % 7);
    Block block(randomBlockType, board.getWidth() / 2 - 1, 0);
    srand(static_cast<unsigned>(time(0)));
    hideCursor();
    board.drawBoard();
    bool gamePaused = false;

    while (true) {
        auto currentTime = std::chrono::high_resolution_clock::now();
        std::chrono::duration<float> elapsed = currentTime - lastTime;

        bool playerMove = false;
        processInput(board, block, playerMove, gamePaused);

        if (gamePaused) {
            pauseGame(board, gamePaused);
            continue;
        }

        if (elapsed.count() >= 0.5) {
            board.removeBlock(block);

            block.moveDown();
            if (board.checkCollision(block)) {
                block.moveUp();
                board.lockBlock(block);
                board.clearWell();
                randomBlockType = static_cast<Block::Type>(rand() % 7);
                block = Block(randomBlockType, board.getWidth() / 2 - 1, 0);
                if (board.checkCollision(block)) {
                    break;
                }
            }

            board.addBlock(block);
            lastTime = currentTime;
        }
        board.updateWell();
    }
}

void hideCursor() {
    HANDLE consoleHandle = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_CURSOR_INFO info;
    info.dwSize = 100;
    info.bVisible = FALSE;
    SetConsoleCursorInfo(consoleHandle, &info);
}

static void processInput(Board& board, Block& block, bool& playerMove, bool& gamePaused) {
    if (_kbhit()) {
        char ch = _getch();
        if (ch == 'q' || ch == 'Q') {
            exit(0);
        }
        else if (ch == 'z' || ch == 'Z') {
            gamePaused = !gamePaused;
        }
        else if (!gamePaused) {
            board.removeBlock(block);
            switch (ch) {
            case 75:
                block.moveLeft();
                if (board.checkCollision(block)) {
                    block.moveRight();
                    playerMove = true;
                }
                break;
            case 77:
                block.moveRight();
                if (board.checkCollision(block)) {
                    block.moveLeft();
                    playerMove = true;
                }
                break;
            case 80:
                block.moveDown();
                if (board.checkCollision(block)) {
                    block.moveUp();
                    playerMove = true;
                }
                break;
            case 72:
                block.rotate();
                if (board.checkCollision(block)) {
                    bool rotatedSuccessfully = false;
                    for (int i = 0; i < 5; ++i) { 
                        if (i == 0) block.moveRight();  
                        else if (i == 1) block.moveLeft();  
                        else if (i == 2) { block.moveLeft(); block.moveLeft(); } 
                        else if (i == 3) { block.moveRight(); block.moveRight(); }  
                        else if (i == 4) { block.moveUp(); }  

                        if (!board.checkCollision(block)) {
                            rotatedSuccessfully = true;
                            break;
                        }

                        
                        if (i == 0) block.moveLeft();
                        else if (i == 1) block.moveRight();
                        else if (i == 2) { block.moveRight(); block.moveRight(); }
                        else if (i == 3) { block.moveLeft(); block.moveLeft(); }
                        else if (i == 4) { block.moveDown(); }
                    }
                    if (!rotatedSuccessfully) {
                        block.rotate(); block.rotate(); block.rotate();  
                    }
                }
                break;
            }
            board.addBlock(block);
        }
    }
}

void pauseGame(Board& board, bool& gamePaused) {
    HANDLE consoleHandle = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(consoleHandle, &csbi);
    int columns = csbi.srWindow.Right - csbi.srWindow.Left + 1;
    int rows = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;

    int pauseMessagePosX = (columns - 102);
    int pauseMessagePosY = (rows - 5);  

    COORD pos;
    pos.X = pauseMessagePosX;
    pos.Y = pauseMessagePosY;
    SetConsoleCursorPosition(consoleHandle, pos);

    std::cout << "Game Paused, Click 'Z' to Resume.";

    while (gamePaused) {
        if (_kbhit()) {
            char ch = _getch();
            if (ch == 'q' || ch == 'Q') {
                exit(0);
            }
            else if (ch == 'z' || ch == 'Z') {
                gamePaused = false;  
                break;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    system("cls");
    board.drawBoard();
}