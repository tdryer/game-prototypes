#ifndef GAMEENTITY_H
#define GAMEENTITY_H

#include <vector>

// forward declaration to prevent cyclic dependency
class Game;

class GameEntity {
public:
    GameEntity(Game *game);
    virtual void update(double millis);
    void draw();
    
    double pos[2], v[2], r, rs, age, radius;
protected:
    virtual void draw_local(double px, double py, double zoom);
    GameEntity * check_collision(std::vector<GameEntity *> *entity_list);
    
    Game *game;
    
};

#endif
