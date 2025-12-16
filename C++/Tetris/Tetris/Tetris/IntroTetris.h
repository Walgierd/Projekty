#pragma once

#include <iostream>
#include <conio.h>
#include <windows.h>
#include <chrono>
#include <thread>

void introTetris() {
    std::string title = "TETRIS";
    std::string instructions[] = {
        "Press ENTER to start game",
        "Press SHIFT for help"
    };
    const int animationDelay = 100; 

    
    system("cls");

    
    HANDLE consoleHandle = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(consoleHandle, &csbi);
    int columns = csbi.srWindow.Right - csbi.srWindow.Left + 1;
    int rows = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;

    int titleStartPos = (columns - title.length()) / 2;
    int instructionsStartPos[2];
    for (int i = 0; i < 2; ++i) {
        instructionsStartPos[i] = (columns - instructions[i].length()) / 2;
    }

    COORD pos;
    pos.X = titleStartPos;
    pos.Y = rows / 2 - 3; 
    SetConsoleCursorPosition(consoleHandle, pos);

    for (char c : title) {
        std::cout << c;
        std::this_thread::sleep_for(std::chrono::milliseconds(animationDelay));
    }

    for (int i = 0; i < 2; ++i) {
        pos.X = instructionsStartPos[i];
        pos.Y += 2;
        SetConsoleCursorPosition(consoleHandle, pos);
        std::cout << instructions[i] << std::endl;
    }

    while (true) {
        if (GetAsyncKeyState(VK_RETURN) & 0x8000) {
            break; 
        }
        else if (GetAsyncKeyState(VK_SHIFT) & 0x8000) {
            system("cls");
            std::cout << "Help:\n";
            std::cout << "Use arrow keys to move the blocks.\n";
            std::cout << "Use up arrow to rotate the block.\n";
            std::cout << "Press Q to quit the game.\n";
            std::cout << "Press Z to pause the game. \n";
            std::cout << "Press ENTER to return to the game.\n";

            while (true) {
                if (GetAsyncKeyState(VK_RETURN) & 0x8000) {
                    system("cls");
                    SetConsoleCursorPosition(consoleHandle, pos);
                    std::cout << instructions[0] << std::endl;
                    pos.Y += 2;
                    SetConsoleCursorPosition(consoleHandle, pos);
                    std::cout << instructions[1] << std::endl;
                    break;
                }
            }
        }
    }

    system("cls"); 
}

void gameOver() {
    std::string gameOverText = "GAME OVER";
    std::string instructions = "Press ENTER to exit";

    system("cls");

    HANDLE consoleHandle = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(consoleHandle, &csbi);
    int columns = csbi.srWindow.Right - csbi.srWindow.Left + 1;
    int rows = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;

    int gameOverStartPos = (columns - gameOverText.length()) / 2;
    int instructionsStartPos = (columns - instructions.length()) / 2;

    COORD pos;
    pos.X = gameOverStartPos;
    pos.Y = rows / 2 - 1;
    SetConsoleCursorPosition(consoleHandle, pos);

    for (char c : gameOverText) {
        std::cout << c;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    pos.X = instructionsStartPos;
    pos.Y += 2;
    SetConsoleCursorPosition(consoleHandle, pos);
    std::cout << instructions << std::endl;

    while (true) {
        if (GetAsyncKeyState(VK_RETURN) & 0x8000) {
            exit(0);
        }
    }
}