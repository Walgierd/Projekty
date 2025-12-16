#pragma once

class Point {
public:
    int x;
    int y;

    Point(int x = 0, int y = 0) : x(x), y(y) {}

    void moveLeft() { x--; }
    void moveRight() { x++; }
    void moveDown() { y++; }
    void moveUp() { y--; }
};