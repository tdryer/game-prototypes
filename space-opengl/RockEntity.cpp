#include "RockEntity.h"

#include <GL/glut.h>
#include <iostream>
#include <cmath>

RockEntity::RockEntity(Game *game, double x, double y) : GameEntity(game) {
    pos[0] = x;
    pos[1] = y;
    
    rs = uniform(-45, 45);
    v[0] = uniform(-10, 10);
    v[1] = uniform(-10, 10);
    
    // create random rock vertices
    num_verts = 8;
    radius = 10;
    verts = new GLfloat[num_verts * 2];
    double radius_min = radius * 0.5;
    double radius_max = radius * 1.5;
    double step = 2 * 3.141 / num_verts;
    for (int i = 0; i < num_verts; i++) {
        double angle = step * i;
        double length = uniform(radius_min, radius_max);
        verts[i*2] = length * sin(angle);
        verts[i*2 + 1] = length * cos(angle);
    }
}

void RockEntity::draw_local(double px, double py, double zoom) {
    glPushMatrix();
	glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
	glVertexPointer(2, GL_FLOAT, 0, verts);
	
	glTranslatef(px, py, 0);
	glScalef(zoom, zoom, 0);
	glRotatef(r, 0, 0, 1);
	
	glDrawArrays(GL_LINE_LOOP, 0, num_verts);
	glPopMatrix();
}

double RockEntity::uniform(double min, double max) {
    return (((double) rand() / RAND_MAX) * (max - min)) + min;
}
