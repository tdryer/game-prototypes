#include "ShipEntity.h"
#include "game.h"

#include <GL/glut.h>
#include <iostream>
#include <cmath>

ShipEntity::ShipEntity(Game *game) : GameEntity(game) {
    radius = 20;
    verts = new GLfloat[num_verts*2];
    verts[0] = -1.0/2;
    verts[1] = -1.0/2;
    verts[2] = 1.0/2;
    verts[3] = -1.0/2;
    verts[4] = 0;
    verts[5] = 1;
    
    fire_verts = new GLfloat[num_verts*2];
    fire_verts[0] = -1.0/4;
    fire_verts[1] = -1.0/2;
    fire_verts[2] = 1.0/4;
    fire_verts[3] = -1.0/2;
    fire_verts[4] = 0;
    fire_verts[5] = -1;
    
    fire_opacity_on = 1.0;
    fire_opacity_off = 0.0;
    fire_opacity = new SmoothStep(1, &fire_opacity_off, 1000);
    
    rotate_left = false;
    rotate_right = false;
    shoot = false;
    thrust = false;
}

void ShipEntity::update(double millis) {
    if (rotate_right) {
        rs = 180;
    }
    else if (rotate_left) {
        rs = -180;
    }
    else {
        rs = 0;
    }
    if (shoot) {
    
    }
    if (thrust) {
        double dv = 100 * (millis/1000);
        v[0] += -1 * dv * sin(r*3.141/180);
        v[1] +=      dv * cos(r*3.141/180);
        
        fire_opacity->set(&fire_opacity_on);
    }
    else {
        fire_opacity->set(&fire_opacity_off);
    }
    
    GameEntity::update(millis);
    
    fire_opacity->update(millis);
    
    // TODO: how to determine if entity is rock?
    GameEntity *e = check_collision(&(game->entities));
    if (e != NULL and e != this) {
        std::cout << "collision\n";
    }
}

void ShipEntity::draw_local(double px, double py, double zoom) {
    glPushMatrix();
	glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
	glVertexPointer(2, GL_FLOAT, 0, verts);
	
	glTranslatef(px, py, 0);
	glScalef(zoom*30, zoom*30, 0);
	glRotatef(r, 0, 0, 1);
	glDrawArrays(GL_LINE_LOOP, 0, num_verts);
	
	if (thrust) {
	    glVertexPointer(2, GL_FLOAT, 0, fire_verts);
	    glColor4f(1.0f, 0.0f, 0.0f, *fire_opacity->get());
	    glDrawArrays(GL_LINE_LOOP, 0, num_verts);
	}
	
	glPopMatrix();
}

