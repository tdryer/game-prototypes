#ifndef SHIPENTITY_H
#define SHIPENTITY_H

#include "GameEntity.h"
#include "SmoothStep.h"

#include <GL/glut.h>

class ShipEntity : public GameEntity {
public:
    ShipEntity(Game *game);
    void update(double millis);
    
    bool rotate_left, rotate_right, shoot, thrust;
    
    
private:
    void draw_local(double px, double py, double zoom);
    
    static const int num_verts = 3;
    GLfloat *verts;
    GLfloat *fire_verts;
    SmoothStep *fire_opacity;
    double fire_opacity_on, fire_opacity_off;
};

#endif
