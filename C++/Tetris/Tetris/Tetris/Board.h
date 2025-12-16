#pragma once
#include "Block.h"
#include <vector>
#include <iostream>

class Board {
private:
    const int boardWidth;
    const int boardHeight;
    std::vector<std::vector<int>> well;

public:
    Board(int w, int h);

    void addBlock(const Block& block);
    void removeBlock(const Block& block);
    void drawBoard() const;
    void clearWell();
    void updateWell();
    bool checkCollision(const Block& block) const;
    void lockBlock(const Block& block);

    int getWidth() const { return boardWidth; }
    int getHeight() const { return boardHeight; }
};

Board::Board(int w, int h) : boardWidth(w), boardHeight(h), well(w, std::vector<int>(h, 0)) {}

void Board::addBlock(const Block& block) {
    for (const auto& point : block.getPoints()) {
        if (point.x >= 0 && point.x < boardWidth && point.y >= 0 && point.y < boardHeight) {
            well[point.x][point.y] = 1;
        }
    }
}

void Board::removeBlock(const Block& block) {
    for (const auto& point : block.getPoints()) {
        if (point.x >= 0 && point.x < boardWidth && point.y >= 0 && point.y < boardHeight) {
            well[point.x][point.y] = 0;
        }
    }
}

void Board::drawBoard() const {
    for (int i = 0; i < 3; ++i) {
        std::cout << std::endl;
    }
    for (int i = 0; i < boardHeight; ++i) {
        std::cout << "                    " << "##";
        for (int j = 0; j < boardWidth; ++j) {
            if (well[j][i] == 1) {
                std::cout << "[]";
            }
            else {
                std::cout << "  ";
            }
        }
        std::cout << "## " << boardHeight - i << std::endl;
    }

    std::cout << "                    ";
    for (int i = 0; i < boardWidth + 2; ++i) {
        std::cout << "##";
    }
    std::cout << std::endl;

    for (int i = 0; i < 3; ++i) {
        std::cout << std::endl;
    }
}

void Board::clearWell() {
    for (int i = 0; i < boardHeight; ++i) {
        bool fullLine = true;
        for (int j = 0; j < boardWidth; ++j) {
            if (well[j][i] != 2) {
                fullLine = false;
                break;
            }
        }
        if (fullLine) {
            for (int k = i; k > 0; --k) {
                for (int j = 0; j < boardWidth; ++j) {
                    well[j][k] = well[j][k - 1];
                }
            }
            for (int j = 0; j < boardWidth; ++j) {
                well[j][0] = 0;
            }
        }
    }
}

void Board::updateWell() {
    std::cout << "\033[4;1H";

    for (int i = 0; i < boardHeight; ++i) {
        std::cout << "                    " << "##";
        for (int j = 0; j < boardWidth; ++j) {
            if (well[j][i] == 1) {
                std::cout << "()";
            }
            else if (well[j][i] == 2) {
                std::cout << "[]";
            }
            else {
                std::cout << "  ";
            }
        }
        std::cout << "## " << boardHeight - i << std::endl;
    }

    std::cout << "                    ";
    for (int i = 0; i < boardWidth + 2; ++i) {
        std::cout << "##";
    }
    std::cout << std::endl;
}

bool Board::checkCollision(const Block& block) const {
    for (const auto& point : block.getPoints()) {
        if (point.x < 0 || point.x >= boardWidth || point.y < 0 || point.y >= boardHeight || well[point.x][point.y] == 2) {
            return true;
        }
    }
    return false;
}

void Board::lockBlock(const Block& block) {
    for (const auto& point : block.getPoints()) {
        if (point.x >= 0 && point.x < boardWidth && point.y >= 0 && point.y < boardHeight) {
            well[point.x][point.y] = 2;
        }
    }
}