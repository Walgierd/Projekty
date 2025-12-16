#pragma once
#include "Point.h"
#include <vector>

class Block : public Point {
public:
    enum class Type { I, J, L, O, S, T, Z };

    Block(Type type, int startX, int startY);

    void moveLeft();
    void moveRight();
    void moveDown();
    void moveUp();
    void rotate();

    const std::vector<Point>& getPoints() const;

private:
    Type type;
    std::vector<Point> points;

    void initializePoints(int startX, int startY);
};

Block::Block(Type type, int startX, int startY) : Point(startX, startY), type(type) {
    initializePoints(startX, startY);
}

void Block::initializePoints(int startX, int startY) {
    points.clear();
    switch (type) {
    case Type::I:
        points = { {startX, startY}, {startX, startY + 1}, {startX, startY + 2}, {startX, startY + 3} };
        break;
    case Type::J:
        points = { {startX, startY}, {startX, startY + 1}, {startX, startY + 2}, {startX - 1, startY + 2} };
        break;
    case Type::L:
        points = { {startX, startY}, {startX, startY + 1}, {startX, startY + 2}, {startX + 1, startY + 2} };
        break;
    case Type::O:
        points = { {startX, startY}, {startX + 1, startY}, {startX, startY + 1}, {startX + 1, startY + 1} };
        break;
    case Type::S:
        points = { {startX, startY}, {startX + 1, startY}, {startX, startY + 1}, {startX - 1, startY + 1} };
        break;
    case Type::T:
        points = { {startX, startY}, {startX - 1, startY + 1}, {startX, startY + 1}, {startX + 1, startY + 1} };
        break;
    case Type::Z:
        points = { {startX, startY}, {startX - 1, startY}, {startX, startY + 1}, {startX + 1, startY + 1} };
        break;
    }
}

void Block::moveLeft() {
    for (auto& point : points) {
        point.moveLeft();
    }
}

void Block::moveRight() {
    for (auto& point : points) {
        point.moveRight();
    }
}

void Block::moveDown() {
    for (auto& point : points) {
        point.moveDown();
    }
}

void Block::moveUp() {
    for (auto& point : points) {
        point.moveUp();
    }
}

void Block::rotate() {
    int centerX = points[1].x;
    int centerY = points[1].y;

    for (auto& point : points) {
        int x = point.x - centerX;
        int y = point.y - centerY;
        point.x = centerX - y;
        point.y = centerY + x;
    }
}

const std::vector<Point>& Block::getPoints() const {
    return points;
}