#ifndef GAME_H
#define GAME_H

#include "SmoothStep.h"
#include "GameEntity.h"
#include "ShipEntity.h"

#include <vector>

enum event_t {KEYDOWN, KEYUP};

class Game {
public:
    
    Game(int width, int height);
    void update(double millis);
    void draw();
    void event(event_t type, unsigned char key);
    
    void grid_to_px(double *x, double *y);
    void px_to_grid(double *x, double *y);
    
    int width, height;
    double left, top, zoom;
    std::vector<GameEntity*> entities;
private:
    void draw_star_layer(double parallax, double brightness);
    
    ShipEntity *ship;
    
    
};

#endif
