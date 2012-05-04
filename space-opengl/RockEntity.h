#ifndef ROCKENTITY_H
#define ROCKENTITY_H

#include "GameEntity.h"

#include <GL/glut.h>

class RockEntity : public GameEntity {
public:
    RockEntity(Game *game, double x, double y);
private:
    void draw_local(double px, double py, double zoom);
    double uniform(double min, double max);
    
    int num_verts;
    GLfloat *verts;
};

#endif
